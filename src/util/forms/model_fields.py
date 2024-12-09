from typing import Any

from django import forms
from django.db.models import Model
from django.utils.translation import gettext_lazy as _

__all__ = (
    'model_field_factory',
    'ModelIntegerField',
    'ModelCharField',
)


def model_field_factory(base_field_class):
    """
    Factory to create a model-aware field from a base field class.
    """
    class _ModelField(base_field_class):
        def __init__(
                self,
                *args,
                model_cls: Model = None,
                extra_filters: dict[str, Any] = None,
                **kwargs
        ):
            self.extra_filters = extra_filters or {}
            if model_cls is None:
                raise ValueError("The `model_cls` parameter is required.")
            self.model_cls = model_cls
            super().__init__(*args, **kwargs)

        def to_python(self, value):
            value = int(value)
            """Convert the input value to a model instance."""
            value = super().to_python(value)
            if value in self.empty_values:
                return None
            try:
                return self.model_cls._default_manager.get(pk=value, **self.extra_filters)
            except self.model_cls.DoesNotExist:
                raise forms.ValidationError(
                    _('The selected %(model_name) does not exist.'),
                    code='invalid',
                    params={'model_name': self.model.__name__},
                )

    return _ModelField


ModelIntegerField = model_field_factory(forms.IntegerField)
ModelCharField = model_field_factory(forms.CharField)
# adicione mais campos conforme o necessário
