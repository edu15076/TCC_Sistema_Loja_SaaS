from django import forms
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit

from loja.forms import BaseFuncionarioCreationForm
from loja.models import Admin
from loja.models import Loja
from util.forms import ModalCrispyFormMixin, CrispyFormMixin

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
        return Submit('submit', _('Save Changes'))

    class Meta:
        model = Loja
        fields = ['nome', 'logo']


class AdminCreationForm(ModalCrispyFormMixin, BaseFuncionarioCreationForm):
    error_messages = BaseFuncionarioCreationForm.error_messages

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('submit', _('Create Admin'))

    class Meta:
        model = Admin
        fields = BaseFuncionarioCreationForm.Meta.fields
        labels = getattr(BaseFuncionarioCreationForm.Meta, 'labels', {})


class FuncionarioGroupForm(CrispyFormMixin, forms.Form):
    group = forms.IntegerField(required=True, widget=forms.HiddenInput)
    funcionario = forms.IntegerField(required=True, widget=forms.HiddenInput)
    action = forms.BooleanField(required=True, widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
