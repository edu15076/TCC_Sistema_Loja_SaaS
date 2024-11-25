from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit

from loja.forms import BaseFuncionarioCreationForm
from loja.models import Admin
from loja.models import Loja
from util.forms import ModalCrispyFormMixin

__all__ = (
    'LojaForm',
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
