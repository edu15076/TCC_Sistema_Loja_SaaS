import unicodedata
from django.db import models
from django.db.models.base import ModelBase

from util.mixins import ModelMetaClassMixin

from .scope import Scope


class AbstractUsernamePerScopeMeta(ModelBase, ModelMetaClassMixin):
    def __new__(cls, name, bases, attrs, **kwargs):
        if cls._is_model_abstract(attrs):
            return super().__new__(cls, name, bases, attrs, **kwargs)

        username_field, found = cls._find_attribute_anywhere(attrs, bases,
                                                             'USERNAME_FIELD')

        if not found:
            raise ValueError('Non abstract subclass or any superclass must define '
                             'USERNAME_FIELD')

        username, found = cls._find_attribute_anywhere(attrs, bases, username_field)

        if not found:
            raise ValueError(f'Non abstract subclass or superclass must define '
                             f'{attrs['USERNAME_FIELD']} for it defined USERNAME_FIELD '
                             f'= {attrs['USERNAME_FIELD']}')

        if 'Meta' in attrs:
            setattr(attrs['Meta'], 'unique_together', ((username_field, 'scope'),))
        else:
            attrs['Meta'] = type('Meta', (),
                                 {'unique_together': ((username_field, 'scope'),)})

        return super().__new__(cls, name, bases, attrs, **kwargs)


class UsernamePerScopeManager(models.Manager):
    def _pop_username_from(self, kwargs):
        return kwargs.pop('username', kwargs.pop(self.model.USERNAME_FIELD, None))

    def _pop_scope_from(self, kwargs):
        scope = kwargs.pop('scope', Scope.scopes.default_scope())
        return scope if scope is not None else Scope.scopes.default_scope()

    def get_by_natural_key(self, **kwargs):
        username = self._pop_username_from(kwargs)
        scope = self._pop_scope_from(kwargs)
        return self.get(**{self.model.USERNAME_FIELD: username, 'scope': scope})

    def create_by_natural_key(self, **kwargs):
        username = self.model.normalize_username(self._pop_username_from(kwargs))
        scope = self._pop_scope_from(kwargs)
        return self.create(**({self.model.USERNAME_FIELD: username, 'scope': scope}
                              | kwargs))

    def get_or_create_by_natural_key(self, **kwargs):
        try:
            return self.get_by_natural_key(**kwargs)
        except self.model.DoesNotExist:
            return self.create_by_natural_key(**kwargs)


class AbstractUsernamePerScope(models.Model, metaclass=AbstractUsernamePerScopeMeta):
    scope = models.ForeignKey(Scope, on_delete=models.CASCADE)

    objects = UsernamePerScopeManager()

    def get_username(self):
        return getattr(self, self.USERNAME_FIELD)

    @classmethod
    def normalize_username(cls, username):
        return (
            unicodedata.normalize("NFKC", username)
            if isinstance(username, str)
            else username
        )

    class Meta:
        abstract = True
