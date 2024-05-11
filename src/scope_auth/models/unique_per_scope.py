from django.db import models
from django.db.models.base import ModelBase

from util.mixins import ModelMetaClassMixin

from .scope import Scope


class UniquePerScopeMeta(ModelBase, ModelMetaClassMixin):
    def __new__(cls, name, bases, attrs, **kwargs):
        if cls._is_model_abstract_from_attrs(attrs):
            return super().__new__(cls, name, bases, attrs, **kwargs)

        cls._add_all_unique_in_scope_as_unique_together(attrs, bases)

        return super().__new__(cls, name, bases, attrs, **kwargs)

    @classmethod
    def _get_unique_in_scope(cls, attrs, bases) -> list:
        all_fields = cls._all_fields_from(attrs, bases)
        unique_in_scope, found = cls._find_attribute(attrs, bases, 'UNIQUE_IN_SCOPE')

        if not found:
            raise ValueError('UNIQUE_IN_SCOPE must be set')

        if not isinstance(unique_in_scope, (list, tuple)):
            raise ValueError('UNIQUE_IN_SCOPE must be a list or tuple')

        for unique_field in unique_in_scope:
            if unique_field not in all_fields:
                raise ValueError(f'{unique_field} is not a field')

        return list(unique_in_scope)

    @classmethod
    def _add_all_unique_in_scope_as_unique_together(cls, attrs, bases):
        # make each UNIQUE_IN_SCOPE fields unique_together with scope
        unique_in_scope = cls._get_unique_in_scope(attrs, bases)

        unique_together = tuple((unique_field, 'scope')
                                for unique_field in unique_in_scope)

        cls._add_unique_together(attrs, unique_together)


class UniquePerScopeModelManager(models.Manager):
    def get_by_natural_key(self, *, scope: Scope = None, **kwargs):
        """
        Returns the instance for the passed atributes
        """
        scope = scope if scope is not None else Scope.scopes.default_scope()
        return self.get(scope=scope, **kwargs)

    def create_by_natural_key(self, *, scope: Scope = None, **kwargs):
        scope = scope if scope is not None else Scope.scopes.default_scope()
        return self.create(scope=scope, **kwargs)


class AbstractUniquePerScopeModel(models.Model, metaclass=UniquePerScopeMeta):
    scope = models.ForeignKey(Scope, on_delete=models.CASCADE)

    UNIQUE_IN_SCOPE = []

    objects = UniquePerScopeModelManager()

    class Meta:
        abstract = True
