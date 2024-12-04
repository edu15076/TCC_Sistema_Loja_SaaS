from django.forms import ValidationError
from .validators import LojaEqualRequiredValidator
from loja.models import Loja

__all__ = (
    'LojaValidatorFormMixin',
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

    def clean(self):
        if not hasattr(self, 'instance') or not self.should_check_model_form:
            return super().clean()
        if self.instance.loja != self.loja:
            raise ValidationError()
        return super().clean()


