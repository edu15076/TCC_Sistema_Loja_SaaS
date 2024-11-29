from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit

from loja.forms import BaseFuncionarioCreationForm
from loja.forms.mixins import LojaValidatorFormMixin
from loja.models import Admin, Funcionario
from loja.models import Loja
from util.forms import ModalCrispyFormMixin, CrispyFormMixin, ModelIntegerField

__all__ = (
    'LojaForm',
    'AdminCreationForm',
    'FuncionarioGroupForm',
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
        'funcionario_dne': _('O funcionário passado não existe'),
        'funcionario_admin': _('You cannot add or remove admins from groups'),
        'cannot_alter_this_funcionario': _('Você não ter permissão para alterar esse funcionario'),
        'group_dne': _('O grupo passado não existe'),
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
    action = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)

    def clean_funcionario(self):
        funcionario = self.cleaned_data.get('funcionario')
        # if funcionario.is_admin:
        #     raise forms.ValidationError(
        #         self.error_messages['funcionario_admin'],
        #         code='funcionario_admin'
        #     )
        # TODO: Verificar se o usuário é admin
        return funcionario

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        group: Group = self.cleaned_data['group']
        action: bool = self.cleaned_data['action']
        if action:
            funcionario.groups.add(group)
        else:
            funcionario.groups.remove(group)
        return action
