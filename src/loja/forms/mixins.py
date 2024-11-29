from django import forms
from django.utils.translation import gettext_lazy as _

from loja.models import Loja

__all__ = (
    'LojaValidatorFormMixin',
    'LojaEqualRequiredValidator',
)


class LojaEqualRequiredValidator:
    """Validator to ensure the object belongs to the specified loja."""
    error_messages = {
        'field_not_from_loja': _('%(field_name) não existe nessa loja'),
    }

    def __init__(self, loja):
        if loja is None:
            raise ValueError("You must specify a 'loja' to use this validator.")
        self.loja = loja

    def __call__(self, value):
        """Validate if the field's value belongs to the correct loja."""
        if value is None:
            return

        try:
            # If it's a model instance, check if the loja matches
            if not hasattr(value, 'loja') or value.loja != self.loja:
                raise forms.ValidationError(
                    self.error_messages['field_not_from_loja'],
                    code='field_not_from_loja',
                    params={'field_name': value.__class__.__name__},
                )
        except AttributeError:
            raise forms.ValidationError(
                _('Invalid field value'),
                code='invalid'
            )


class LojaValidatorFormMixin:
    fields_loja_check: list[str] = []

    def __init__(self, *args, loja: Loja = None, **kwargs):
        super().__init__(*args, **kwargs)
        if loja is None:
            raise ValueError(
                "The `loja` parameter is required for LojaValidatorMixin."
            )
        self.loja = loja
        for field in self.fields_loja_check:
            self.fields[field].validators.append(LojaEqualRequiredValidator(loja=loja))



