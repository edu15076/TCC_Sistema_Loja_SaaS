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



