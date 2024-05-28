from django.db import models
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor

from .metaclass_mixin import MetaClassMixin


class ModelMetaClassMixin(MetaClassMixin):
    @classmethod
    def _get_fields_names(cls, fields):
        return {field.name for field in fields}

    @classmethod
    def _has_field(cls, self, field_name: str) -> bool:
        return field_name in cls._get_fields_names(self._meta.fields)

    @classmethod
    def _find_field_for_name(
        cls, self, field_name: str
    ) -> tuple[models.Field | None, bool]:
        for field in self._meta.fields:
            if field_name == field.name:
                return field, True
        return None, False

    @classmethod
    def _is_model_abstract_from_attrs(cls, attrs) -> bool:
        return 'Meta' in attrs and getattr(attrs['Meta'], 'abstract', None)

    @classmethod
    def _all_fields_from(cls, attrs, bases):
        all_attrs = cls._all_attributes(attrs, bases)
        return {
            name: attr
            for name, attr in all_attrs.items()
            if isinstance(attr, (models.Field, ForwardManyToOneDescriptor))
        }

    @classmethod
    def _add_field_to_meta(cls, attrs, name: str, value):
        if 'Meta' in attrs:
            setattr(attrs['Meta'], name, value)
        else:
            attrs['Meta'] = type('Meta', (), {name: value})

    @classmethod
    def _add_unique_together(cls, attrs, unique_together):
        previous_unique_together = (
            tuple()
            if 'Meta' not in attrs
            else getattr(attrs['Meta'], 'unique_together', tuple())
        )

        cls._add_field_to_meta(
            attrs, 'unique_together', previous_unique_together + unique_together
        )
