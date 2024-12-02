import abc
from abc import ABC
from contextlib import suppress

from django.contrib.auth.models import Group
from django.http import HttpResponseNotFound, JsonResponse
from django.views.generic import ListView, DetailView, FormView

from saas.models import ClienteContratante
from util.views import HTMXHelperMixin, HTMXFormMixin
from common.views import CreateUsuarioGenericoView
from loja.forms import (
    FuncionarioIsActiveForm,
    FuncionarioPapelForm,
    FuncionarioCreationForm
)
from loja.models import Funcionario

__all__ = (
    'FuncionarioContextDataMixin',
    'ABCListFuncionariosView',
    'ABCCardFuncionarioView',
    'ABCCriarFuncionarioView',
    'ABCTrocarFuncionarioIsValidView',
    'ABCDesativarFuncionarioView',
    'ABCReativarFuncionarioView',
    'ABCTrocarPapelFuncionarioView',
    'ABCAdicionarPapelFuncionarioView',
    'ABCRemoverPapelFuncionarioView',
)


class FuncionarioContextDataMixin:
    def pode_trocar_papeis(self, funcionario: Funcionario) -> bool:
        return not funcionario.is_admin

    def pode_trocar_is_active(self, funcionario: Funcionario) -> bool:
        return True

    def _get_papeis(self, funcionario: Funcionario, action: bool, groups):
        if not self.pode_trocar_papeis(funcionario):
            return groups.values('name', 'pk')
        return [
            group | {
                'form': FuncionarioPapelForm(
                    initial={
                        'group': group['pk'],
                        'funcionario': funcionario.pk,
                        'action': action,
                    },
                    loja=self.user.loja,
                    auto_id=f'change-funcionario-papel-'
                            f'{funcionario.pk}-group-{group['pk']}-%s'
                )
            } for group in groups.values('name', 'pk')
        ]

    def get_papeis_pertence(self, funcionario: Funcionario):
        return self._get_papeis(funcionario, False, funcionario.groups.all())

    def get_papeis_nao_pertence(self, funcionario: Funcionario):
        return self._get_papeis(funcionario, True, funcionario.not_in_groups())

    def get_is_active_change_form(self, funcionario: Funcionario):
        if not self.pode_trocar_is_active(funcionario):
            return None
        return FuncionarioIsActiveForm(
            initial={
                'funcionario': funcionario.pk,
                'is_active': not funcionario.is_active,
            },
            loja=self.user.loja,
            auto_id=f'change-is-active-funcionario-{funcionario.pk}-%s'
        )

    def get_context_data_funcionario(self, funcionario: Funcionario):
        funcionario.papeis_pertence = self.get_papeis_pertence(funcionario)
        funcionario.papeis_nao_pertence = self.get_papeis_nao_pertence(funcionario)
        funcionario.is_active_change_form = self.get_is_active_change_form(funcionario)
        return funcionario

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups')


class ABCListFuncionariosView(
    FuncionarioContextDataMixin, HTMXHelperMixin, ListView, ABC
):
    template_name = 'gestao_funcionarios/includes/list_funcionarios.html'
    model = Funcionario
    # TODO: fix pagination paginate_by = 20
    restrict_direct_access = True
    context_object_name = 'funcionarios'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for funcionario in context['funcionarios']:
            self.get_context_data_funcionario(funcionario)
        return context

    @property
    @abc.abstractmethod
    def user(self) -> Funcionario | ClienteContratante:
        raise NotImplementedError


class ABCCardFuncionarioView(
    FuncionarioContextDataMixin, HTMXHelperMixin, DetailView, ABC
):
    template_name = 'gestao_funcionarios/cards/card_funcionario.html'
    restrict_direct_access = True
    model = Funcionario
    context_object_name = 'funcionario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_context_data_funcionario(context['funcionario'])
        return context

    @property
    @abc.abstractmethod
    def user(self) -> Funcionario | ClienteContratante:
        raise NotImplementedError


class ABCCriarFuncionarioView(
    CreateUsuarioGenericoView, ABC
):
    model = Funcionario
    form_class = FuncionarioCreationForm
    template_name = (
        'gestao_funcionarios/modals/includes/modal_generic_criar_funcionario.html'
    )
    form_template_name = 'gestao_funcionarios/forms/htmx_create_funcionario.html'
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True
    login_valid_user = False
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'auto_id': 'id_create_funcionario_%s'}

    def get_created_user_scope(self):
        return self.user.loja.scope

    @property
    @abc.abstractmethod
    def user(self) -> Funcionario | ClienteContratante:
        raise NotImplementedError


class ABCTrocarFuncionarioIsValidView(
    HTMXFormMixin, FormView, ABC
):
    form_class = FuncionarioIsActiveForm
    redirect_on_success = False
    success_url = None
    is_active_next = False

    def get(self, *args, **kwargs):
        return HttpResponseNotFound()

    def get_success_url_kwargs(self) -> dict:
        return {
            'pk': self.form.cleaned_data['funcionario'].pk,
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'is_active_next': self.is_active_next,
        }

    def get_form(self, form_class=None):
        if not hasattr(self, 'form'):
            setattr(self, 'form', super().get_form(form_class))
        return self.form

    def form_invalid(self, form):
        # TODO: posteriormente alterar isso para mostrar um erro
        return JsonResponse({'status': True}, status=422)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    @property
    @abc.abstractmethod
    def user(self) -> Funcionario | ClienteContratante:
        raise NotImplementedError


class ABCDesativarFuncionarioView(ABCTrocarFuncionarioIsValidView, ABC):
    is_active_next = False


class ABCReativarFuncionarioView(ABCTrocarFuncionarioIsValidView, ABC):
    is_active_next = True


class ABCTrocarPapelFuncionarioView(
    HTMXFormMixin, FormView, ABC
):
    form_class = FuncionarioPapelForm
    action = True
    redirect_on_success = False
    success_url = None

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        with suppress(Group.DoesNotExist):
            context_data['group'] = Group.objects.get(pk=self.kwargs.get('group'))
        context_data['funcionario_pk'] = str(self.kwargs.get('funcionario'))
        return context_data

    def get_initial(self):
        return {
            'group': self.kwargs.get('group'),
            'funcionario': self.kwargs.get('funcionario'),
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'action': self.action,
        }

    def get_success_url_kwargs(self) -> dict:
        return {
            'group': self.form.cleaned_data['group'].pk,
            'funcionario': self.form.cleaned_data['funcionario'].pk,
        }

    def get_form(self, form_class=None):
        if not hasattr(self, 'form'):
            setattr(self, 'form', super().get_form(form_class))
        return self.form

    def form_invalid(self, form):
        # TODO: posteriormente alterar isso para mostrar um erro
        return JsonResponse({'status': True}, status=422)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    @property
    @abc.abstractmethod
    def user(self) -> Funcionario | ClienteContratante:
        raise NotImplementedError


class ABCAdicionarPapelFuncionarioView(ABCTrocarPapelFuncionarioView, ABC):
    template_name = 'gestao_funcionarios/pills/pill_adicionar_papel.html'
    form_action_name = 'adicionar_papel_action'
    action = True


class ABCRemoverPapelFuncionarioView(ABCTrocarPapelFuncionarioView, ABC):
    template_name = 'gestao_funcionarios/pills/pill_remover_papel.html'
    form_action_name = 'remover_papel_action'
    action = False
