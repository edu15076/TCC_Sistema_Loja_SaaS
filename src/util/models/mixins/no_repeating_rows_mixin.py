from django.db import models
from django.db.models.base import ModelBase

from util.mixins import ModelMetaClassMixin


class NoRepeatingRowsMixinMeta(ModelBase, ModelMetaClassMixin):
    def __new__(cls, name, bases, attrs, **kwargs):
        if cls._is_model_abstract_from_attrs(attrs):
            return super().__new__(cls, name, bases, attrs, **kwargs)

        cls._add_all_unique_together(attrs, bases)

        return super().__new__(cls, name, bases, attrs, **kwargs)

    @classmethod
    def _add_all_unique_together(cls, attrs, bases):
        # make all fields unique_together
        all_fields = cls._all_fields_from(attrs, bases)
        unique_together = (tuple(name for name in all_fields),)

        cls._add_unique_together(attrs, unique_together)


class NoRepeatingRowsMixin(models.Model, metaclass=NoRepeatingRowsMixinMeta):
    """
    This mixin add a unique_together for all fields in the inherit model.

    You'd better not use this mixin if you have a row with unique=True and null=False.
    Remember that pk is usually auto-set as id.
    """

    class Meta:
        abstract = True
