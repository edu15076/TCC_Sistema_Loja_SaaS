from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Contrato 

class QuebrarContratoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Cancelar contrato')))

    def save(self, commit: bool = True) -> Any:
        contrato = super().save(commit=False)

        if commit:
            contrato.save()
            
        return contrato