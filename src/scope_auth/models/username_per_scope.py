import unicodedata

from .scope import Scope
from .unique_per_scope import (UniquePerScopeModelManager, UniquePerScopeMeta,
                               AbstractUniquePerScopeModel)


class UsernamePerScopeMeta(UniquePerScopeMeta):
    def __new__(cls, name, bases, attrs, **kwargs):
        if cls._is_model_abstract_from_attrs(attrs):
            return super().__new__(cls, name, bases, attrs, **kwargs)

        username_field, found = cls._find_attribute(attrs, bases, 'USERNAME_FIELD')

        if not found:
            raise ValueError('Non abstract subclass or any superclass must define '
                             'USERNAME_FIELD')

        unique_in_scope = cls._get_unique_in_scope(attrs, bases)

        if username_field not in unique_in_scope:
            unique_in_scope.append(username_field)

        attrs['UNIQUE_IN_SCOPE'] = unique_in_scope

        self = super().__new__(cls, name, bases, attrs, **kwargs)
        if self._meta.abstract:
            return self

        username, found = cls._find_field_for_name(self, username_field)

        if not found:
            raise ValueError(f'Non abstract subclass or superclass must define '
                             f'{attrs['USERNAME_FIELD']} for it defined USERNAME_FIELD '
                             f'= {attrs['USERNAME_FIELD']}')

        return self


class UsernamePerScopeManager(UniquePerScopeModelManager):
    def _pop_username_from(self, kwargs):
        return kwargs.pop('username', kwargs.pop(self.model.USERNAME_FIELD, None))

    def get_by_natural_key(self, *, scope: Scope = None, **kwargs):
        username = self._pop_username_from(kwargs)
        return super().get_by_natural_key(scope=scope,
                                          **({self.model.USERNAME_FIELD: username}
                                             | kwargs))

    def create_by_natural_key(self, *, scope: Scope = None, **kwargs):
        username = self.model.normalize_username(self._pop_username_from(kwargs))
        return super().create_by_natural_key(scope=scope,
                                             **({self.model.USERNAME_FIELD: username}
                                                | kwargs))

    def get_or_create_by_natural_key(self, **kwargs):
        try:
            return self.get_by_natural_key(**kwargs)
        except self.model.DoesNotExist:
            return self.create_by_natural_key(**kwargs)


class AbstractUsernamePerScope(AbstractUniquePerScopeModel,
                               metaclass=UsernamePerScopeMeta):
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
