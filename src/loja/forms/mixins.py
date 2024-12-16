from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import QuerySet

from .validators import LojaEqualRequiredValidator
from loja.models import Loja

__all__ = ('LojaValidatorFormMixin',)


class LojaValidatorFormMixin:
    error_messages = {
        'element_not_from_loja': _('alguns %(field_name) não existem nessa loja'),
        'instance_not_from_loja':
            _('Instância de %(instance_type)s não existe nessa loja'),
    }
    fields_loja_check: list[str] = []
    should_check_model_form: bool = True

    def __init__(self, *args, loja: Loja = None, **kwargs):
        super().__init__(*args, **kwargs)
        if loja is None:
            raise ValueError("The `loja` parameter is required for LojaValidatorMixin.")
        self.loja = loja
        for field in self.fields_loja_check:
            if not issubclass(type(self.fields[field]), forms.ModelMultipleChoiceField):
                self.fields[field].validators.append(
                    LojaEqualRequiredValidator(loja=loja)
                )

    def clean(self):
        for field in self.fields_loja_check:
            if (
                issubclass(type(self.cleaned_data[field]), QuerySet)
                and self.cleaned_data[field].exclude(loja=self.loja).exists()
            ):
                raise forms.ValidationError(
                    self.error_messages['element_not_from_loja'],
                    code='element_not_from_loja',
                    params={'field_name': field},
                )

        if not hasattr(self, 'instance') or not self.should_check_model_form:
            return super().clean()
        if self.instance.loja != self.loja:
            raise forms.ValidationError(
                self.error_messages['instance_not_from_loja'],
                code='instance_not_from_loja',
                params={'instance_type': self.instance.__class__.__name__},
            )
        return super().clean()
