from django.contrib.auth.mixins import PermissionRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from . import UserFromLojaRequiredMixin
from .abstract import (
    ABCListFuncionariosView,
    ABCCardFuncionarioView,
    ABCCriarFuncionarioView,
    ABCTrocarFuncionarioIsValidView,
    ABCDesativarFuncionarioView,
    ABCReativarFuncionarioView,
    ABCTrocarPapelFuncionarioView,
    ABCAdicionarPapelFuncionarioView,
    ABCRemoverPapelFuncionarioView, FuncionarioContextDataMixin
)
from ..forms import NonAdminFuncionarioIsActiveForm
from ..models import GerenteDeRH, Funcionario
from ..views import LojaProtectionMixin


__all__ = (
    'ListFuncionariosView',
    'CardFuncionarioView',
    'CriarFuncionarioView',
    'TrocarFuncionarioIsValidView',
    'DesativarFuncionarioView',
    'ReativarFuncionarioView',
    'AdicionarPapelFuncionarioView',
    'RemoverPapelFuncionarioView',
    'GestaoFuncionariosView',
)


# TODO: adicionar permissoes permission_required = 'loja.gerir_funcionarios_da_loja'


class FuncionarioContextDataControlledMixin(FuncionarioContextDataMixin):
    def pode_trocar_papeis(self, funcionario: Funcionario) -> bool:
        return not funcionario.is_admin and funcionario != self.user

    def pode_trocar_is_active(self, funcionario: Funcionario) -> bool:
        return not funcionario.is_admin and funcionario != self.user


class ListFuncionariosView(
    LojaProtectionMixin,
    FuncionarioContextDataControlledMixin,
    ABCListFuncionariosView
):
    template_name = 'gestao_funcionarios/includes/list_funcionarios.html'

    ordering = ['-is_active', 'is_admin', 'nome']

    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CardFuncionarioView(
    LojaProtectionMixin,
    FuncionarioContextDataControlledMixin,
    ABCCardFuncionarioView
):
    template_name = 'gestao_funcionarios/cards/card_funcionario.html'

    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CriarFuncionarioView(
    LojaProtectionMixin, ABCCriarFuncionarioView
):
    template_name = 'gestao_funcionarios/modals/modal_criar_funcionario.html'

    usuario_class = GerenteDeRH

    def get_form_action(self):
        return reverse('criar_funcionario', kwargs={'loja_scope': int(self.scope)})

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse(
            'funcionario_detail',
            kwargs={'pk': self.object.pk, 'loja_scope': int(self.scope)}
        )


class TrocarFuncionarioIsValidView(
    UserFromLojaRequiredMixin, ABCTrocarFuncionarioIsValidView
):
    form_class = NonAdminFuncionarioIsActiveForm

    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse('funcionario_detail', kwargs=self.get_success_url_kwargs())

    def get_success_url_kwargs(self) -> dict:
        return super().get_success_url_kwargs() | {'loja_scope': int(self.scope)}

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'user': self.user}


class DesativarFuncionarioView(
    TrocarFuncionarioIsValidView, ABCDesativarFuncionarioView
):
    pass


class ReativarFuncionarioView(
    TrocarFuncionarioIsValidView, ABCReativarFuncionarioView
):
    pass


class TrocarPapelFuncionarioView(
    UserFromLojaRequiredMixin, ABCTrocarPapelFuncionarioView
):
    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url_kwargs(self):
        return super().get_success_url_kwargs() | {'loja_scope': int(self.scope)}

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'user': self.user}


class AdicionarPapelFuncionarioView(
    TrocarPapelFuncionarioView, ABCAdicionarPapelFuncionarioView
):
    def get_form_action(self):
        return reverse('adicionar_papel', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse('remover_papel', kwargs=self.get_success_url_kwargs())


class RemoverPapelFuncionarioView(
    TrocarPapelFuncionarioView, ABCRemoverPapelFuncionarioView
):
    def get_form_action(self):
        return reverse('remover_papel', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse('adicionar_papel', kwargs=self.get_success_url_kwargs())


class GestaoFuncionariosView(
    UserFromLojaRequiredMixin, TemplateView
):
    template_name = 'gestao_funcionarios/gestao_funcionarios.html'
    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})
