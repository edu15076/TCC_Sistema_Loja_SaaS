from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _

from common.forms import UsuarioGenericoPessoaFisicaCreationForm
from util.forms import ModalCrispyFormMixin, CrispyFormMixin, ModelIntegerField
from .validators import NotAdminValidator, ActiveFuncionarioValidator, SelfValidator
from .mixins import LojaValidatorFormMixin
from ..models import Funcionario

__all__ = (
    'BaseFuncionarioCreationForm',
    'FuncionarioCreationForm',
    'FuncionarioPapelForm',
    'FuncionarioIsActiveForm',
    'NonAdminFuncionarioIsActiveForm',
)


class BaseFuncionarioCreationForm(UsuarioGenericoPessoaFisicaCreationForm):
    error_messages = UsuarioGenericoPessoaFisicaCreationForm.error_messages

    class Meta:
        model = Funcionario
        fields = UsuarioGenericoPessoaFisicaCreationForm.Meta.fields
        labels = getattr(UsuarioGenericoPessoaFisicaCreationForm.Meta, 'labels', {})


class FuncionarioCreationForm(ModalCrispyFormMixin, BaseFuncionarioCreationForm):
    error_messages = BaseFuncionarioCreationForm.error_messages

    def get_submit_button(self) -> Submit:
        return Submit('create_funcionario', _('Criar Funcionário'))

    class Meta:
        model = Funcionario
        fields = BaseFuncionarioCreationForm.Meta.fields
        labels = getattr(BaseFuncionarioCreationForm.Meta, 'labels', {})


class FuncionarioPapelForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    error_messages = {
        'funcionario_admin': _('You cannot add or remove admins from groups'),
    }
    fields_loja_check = ['funcionario']

    group = ModelIntegerField(
        required=True, widget=forms.HiddenInput, model_cls=Group, extra_filters={
            'name__startswith': 'loja_'
        }
    )
    funcionario = ModelIntegerField(
        required=True,
        widget=forms.HiddenInput,
        model_cls=Funcionario,
        validators=[NotAdminValidator(), ActiveFuncionarioValidator()],
    )

    def __init__(self, *args, action: bool = False, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.action = action
        self.fields['funcionario'].validators.append(SelfValidator(user))

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        group: Group = self.cleaned_data['group']
        if self.action:
            funcionario.adicionar_papel(group)
        else:
            funcionario.remover_papel(group)
        return self.action


class FuncionarioIsActiveForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    fields_loja_check = ['funcionario']

    funcionario = ModelIntegerField(
        required=True, widget=forms.HiddenInput, model_cls=Funcionario
    )

    def __init__(self, *args, is_active_next: bool = False, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.is_active_next = is_active_next
        self.fields['funcionario'].validators.append(SelfValidator(user))

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        if self.is_active_next:
            funcionario.reactivate()
        else:
            funcionario.deactivate()
        return self.is_active_next


class NonAdminFuncionarioIsActiveForm(FuncionarioIsActiveForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['funcionario'].validators.append(NotAdminValidator())
