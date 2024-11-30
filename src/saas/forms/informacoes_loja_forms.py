from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit, Layout, Field

from loja.forms import BaseFuncionarioCreationForm
from loja.forms.mixins import LojaValidatorFormMixin
from loja.models import Admin, Funcionario
from loja.models import Loja
from util.forms import ModalCrispyFormMixin, CrispyFormMixin, ModelIntegerField

__all__ = (
    'LojaForm',
    'AdminCreationForm',
    'FuncionarioGroupForm',
    'IsAdminForm',
    'IsActiveFuncionarioForm',
)


class LojaForm(ModalCrispyFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('update_loja', _('Save Changes'))

    class Meta:
        model = Loja
        fields = ['nome', 'logo']


class AdminCreationForm(ModalCrispyFormMixin, BaseFuncionarioCreationForm):
    error_messages = BaseFuncionarioCreationForm.error_messages

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('create_admin', _('Create Admin'))

    class Meta:
        model = Admin
        fields = BaseFuncionarioCreationForm.Meta.fields
        labels = getattr(BaseFuncionarioCreationForm.Meta, 'labels', {})


class FuncionarioGroupForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
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
        required=True, widget=forms.HiddenInput, model_cls=Funcionario
    )

    def __init__(self, *args, action: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.action = action

    def clean_funcionario(self):
        funcionario = self.cleaned_data.get('funcionario')
        if funcionario.is_admin:
            raise forms.ValidationError(
                self.error_messages['funcionario_admin'],
                code='funcionario_admin'
            )
        return funcionario

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        group: Group = self.cleaned_data['group']
        if self.action:
            funcionario.adicionar_papel(group)
        else:
            funcionario.remover_papel(group)
        return self.action


class IsAdminForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    fields_loja_check = ['funcionario']

    funcionario = ModelIntegerField(
        required=True, widget=forms.HiddenInput, model_cls=Funcionario
    )
    is_admin = forms.BooleanField(
        required=False,
        label=_('Admin'),
        widget=forms.CheckboxInput(attrs={
            'class': 'is-admin-checkbox-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.helper.layout = Layout(
            'funcionario',
            Field('is_admin', wrapper_class='form-switch'),
        )

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        is_admin: bool = self.cleaned_data['is_admin']
        funcionario.is_admin = is_admin
        if is_admin:
            Admin.grant_admin(funcionario)
        else:
            Admin.revoque_admin(funcionario)
        return is_admin


class IsActiveFuncionarioForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    fields_loja_check = ['funcionario']

    funcionario = ModelIntegerField(
        required=True, widget=forms.HiddenInput, model_cls=Funcionario
    )

    def __init__(self, *args, is_active_next: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.is_active_next = is_active_next

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        if self.is_active_next:
            funcionario.reactivate()
        else:
            funcionario.deactivate()
        return self.is_active_next
