from collections.abc import Sequence
from typing import Any

from django.db.models.query import QuerySet
from django import forms
from django.views.generic.list import MultipleObjectMixin
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from django.views.generic.base import View
from django.http import Http404, HttpResponseForbidden
from django.utils.translation import gettext as _

from django.core.exceptions import ImproperlyConfigured
from django.core.exceptions import FieldError

from util.logging import Loggers


class MultipleObjectFilterMixin(MultipleObjectMixin):
    """
    Mixin para views poderem lidar, exibir e filtrar listas
    de objetos.
    """

    url_filter_kwargs = None
    user_attribute_name = None
    filter_form = None

    def url_kwargs_erro(self, exception: Exception = None, message: str = None):
        """
        Determina o que fazer quando há erro nos kwargs de url defindos.
        """

        if message is None:
            message = _(
                (
                    f"Erro no parametro '{exception.args[0]}' "
                    f"definido em '{self.__class__.__name__}"
                    f".url_filter_kwargs'"
                )
            )

        Loggers.DEBUG_VERBOSE.value().exception(msg=message)
        raise Http404(_("Pagina invalida"))

    def get_filter_parameters(self) -> dict[str, Any]:
        """
        Recupera os parametros para filtrar o queryset com valores
        recebidos pelo `filter_form`

        :return: dicionário com o nome do campo e o valor a ser filtrado
        """

        form = self.filter_form(self.request.GET)

        if not form.is_valid():
            return {}

        parameters = form.cleaned_data

        try:
            filter_arguments = self.filter_form.filter_arguments

            if filter_arguments is None:
                return {}

            if isinstance(filter_arguments, dict):
                for key, value in filter_arguments.items():
                    parameters[value] = parameters.pop(key)

                for key in self.filter_form.order_arguments:
                    parameters.pop(key)
            elif isinstance(filter_arguments, list):
                cleaned_parameters = {}
                for key in filter_arguments:
                    cleaned_parameters[key] = parameters[key]
                parameters = cleaned_parameters
            else:
                raise ImproperlyConfigured(
                    _((
                            f"'{self.__class__.__name__}.filter_form.filter_arguments'"
                            f" is not type dict or list"
                    ))
                )

        except AttributeError:
            pass

        return parameters

    def get_order_parameters(self) -> list[str]:
        """
        Recupera os parametros para ordenar o queryset
        com valores recebidos pelo `filter_form`

        :return: lista com os argumentos usados na ordenação do queryset
        """

        form = self.filter_form(self.request.GET)

        if not form.is_valid():
            return []

        parameters = []

        try:
            if self.filter_form.order_arguments is None:
                return []

            if not isinstance(self.filter_form.order_arguments, list):
                raise ImproperlyConfigured(
                    "'self.filter_form.order_arguments' is not type list"
                )

            for param in self.filter_form.order_arguments:
                parameters.append(form.cleaned_data[param])
        except AttributeError:
            return []

        return parameters

    def get_ordering(self) -> Sequence[str]:
        """
        :return: lista com os usados para ordernar o queryset, se houver filter_form
        irá retornar o resultado de `self.get_order_parameters()`
        """

        if self.filter_form is None:
            return super().get_ordering()

        ordering = self.get_order_parameters()

        if len(ordering) == 0:
            return super().get_ordering()

        return ordering

    def get_url_filter_kwargs(self) -> dict[str, Any]:
        """
        Obtem dicionário com os arguementos de filtro definidos na url,
        listados em `self.url_filter_kwargs`

        :return: dicionário com nome do campo que será filtrado e valor
        """

        try:
            params = None

            if isinstance(self.url_filter_kwargs, dict):
                params = {
                    key: self.kwargs[value]
                    for key, value in self.url_filter_kwargs.items()
                }
            elif isinstance(self.url_filter_kwargs, list):
                params = {key: self.kwargs[key] for key in self.url_filter_kwargs}

            return params
        except KeyError as e:
            self.url_kwargs_erro(
                exception=e,
                message=_(
                    (
                        f"Configuração invalida do atributo "
                        f"'{self.__class__.__name__}.url_filter_kwargs'"
                        f", valor não correponde a chaves do "
                        f"'self.kwargs'."
                    )
                ),
            )

    def get_user(self):
        """Retorna o usuário logado"""
        return self.request.user

    def get_queryset(self) -> QuerySet[Any]:
        """
        Retorna a lista de itens do model da view filtrada pelo formulário
        `self.filter_form` e pelos argumentos de url, alem de filtrar pelo 
        atributo de usuário do model definido em `self.user_attribute_name`,
        se definido, com o usuário retornado por `self.get_user()`.
        
        Também define `self.queryset` com o valor de retorno.

        :return: lista de itens do modelo
        """
        queryset = super().get_queryset()

        try:
            url_params = self.get_url_filter_kwargs()

            if url_params is not None:
                queryset = queryset.filter(**url_params)
        except (KeyError, FieldError) as e:
            self.url_kwargs_erro(
                message=_(
                    (
                        f"Erro ao filtrar queryset com os argumentos "
                        f"passados por {self.__class__.__name__}"
                        f".url_filter_kwargs."
                    )
                ),
                exception=e,
            )

        if issubclass(self.filter_form, forms.BaseForm):
            filter_params = self.get_filter_parameters()
            order_params = self.get_ordering()

            queryset = queryset.filter(**filter_params)

            if isinstance(order_params, list):
                queryset = queryset.order_by(*order_params)

        if self.user_attribute_name is not None:
            queryset = queryset.filter(**{self.user_attribute_name: self.get_user()})

        # self.object_list = queryset
        self.queryset = queryset
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)

        if self.filter_form is not None:
            context['filter_form'] = self.filter_form()

        return context


class BaseFilterListView(MultipleObjectFilterMixin, View):
    """View base que exibe listas de objetos com filtros"""

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        allow_empty = self.allow_empty()

        if not allow_empty:
            if self.get_paginate_by(self.object_list) is not None and hasattr(
                self.object_list, 'exists'
            ):
                is_empty = not self.object_list.exists()
            else:
                is_empty = not self.object_list

            if is_empty:
                raise Http404(
                    _("Empty list and “%(class_name)s.allow_empty” is False.")
                    % {
                        "class_name": self.__class__.__name__,
                    }
                )

        context = self.get_context_data()
        return self.render_to_response(context)


class FilterListView(MultipleObjectTemplateResponseMixin, BaseFilterListView):
    """
    Renderiza a lista de objetos definida por `self.model` ou `self.queryset`.
    Permite filtrar essa lista por variaveis definidas na url e
    recuperadas por `self.url_filter_kwargs` ou pelos dados do formulário
    de filtro, definido por `self.filter_form`. Esse segundo também permite
    ordenar quando se define o atributo `self.filter_form.order_arguments`.
    """
