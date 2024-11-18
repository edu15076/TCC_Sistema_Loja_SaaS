from typing import Any, Union

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.views.generic.edit import ModelFormMixin, ProcessFormView
from django.views.generic.list import MultipleObjectTemplateResponseMixin
from django.http import Http404
from django.forms.models import model_to_dict
from django.utils.translation import gettext as _

from .filter_list import BaseFilterListView
from .htmx import HTMXModelFormMixin


class BaseCreateOrUpdateListView(BaseFilterListView, ModelFormMixin, ProcessFormView):
    template_name_suffix = '_create_update'

    def get_pk_slug(self) -> tuple[Union[int, None], Union[str, None]]:
        """
        :return: o pk e a slug recuperados da url ou `None`
        se for um requisiçao para criar ou visualizar os dados
        """

        pk = self.kwargs.get(self.pk_url_kwarg)
        slug = self.kwargs.get(self.slug_url_kwarg)

        return (pk, slug)

    def get_object(self, queryset: QuerySet[Any] | None = None):
        """
        :return: o objeto que esta sendo selecionado por pk ou slug ou None
        """

        if queryset is None:
            queryset = self.get_queryset()

        pk, slug = self.get_pk_slug()

        if pk is not None:
            queryset = queryset.filter(pk=pk)

        if slug is not None and (pk is None or self.query_pk_and_slug):
            slug_field = self.get_slug_field()
            queryset = queryset.filter(**{slug_field: slug})

        try:
            if pk is None and slug is None:
                self.object = None
            else:
                self.object = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(
                _(
                    (
                        f"Não foi encontrado nenhum "
                        f"{queryset.model._meta.verbose_name}"
                        f" correspondendo a consulta"
                    )
                )
            )

        return self.object

    def get(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        self.object_list = self.get_queryset()
        self.object = self.get_object()
        allow_empty = self.get_allow_empty()

        if not allow_empty and len(self.object_list) == 0:
            raise Http404(
                _(
                    (
                        f"Não encontrados objetos correspondentes"
                        f"{self.queryset.model._meta.verbose_name}s"
                    )
                )
            )

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object_list=self.object_list, form=form)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        self.object_list = self.get_queryset()

        return self.render_to_response(
            self.get_context_data(object_list=self.object_list, form=form)
        )

    def get_data(self):
        return model_to_dict(self.object)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True, 'data': self.get_data()}, status=200)


class CreateOrUpdateListView(
    BaseCreateOrUpdateListView, MultipleObjectTemplateResponseMixin
):
    """
    View que permite visualizar uma lista de objetos, cadastrar e editar eles
    """


class CreateOrUpdateListHTMXView(
    HTMXModelFormMixin,
    BaseCreateOrUpdateListView,
    MultipleObjectTemplateResponseMixin,
):
    """
    View que permite visualizar uma lista de objetos, cadastrar e editar eles
    usando HTMX
    """

    def form_invalid(self, form):
        return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    def form_valid(self, form):
        self.object = form.save()
        return JsonResponse({'success': True, 'data': self.get_data()}, status=200)
