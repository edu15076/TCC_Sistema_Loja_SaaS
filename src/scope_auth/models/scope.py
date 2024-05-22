import functools

from django.db import models
from django.db.models import Q

from util.decorators import CachedClassProperty
from util.models import AbstractSingleton


class ScopeManager(models.Manager):
    def all_but_default(self):
        return self.filter(~Q(id=DefaultScope.instance_pk))

    @functools.cache
    def default_scope(self):
        return DefaultScope.instance.base_scope


class Scope(models.Model):
    scope = models.BigAutoField(primary_key=True, serialize=False, verbose_name='ID')

    scopes = ScopeManager()

    def __int__(self, *args, **kwargs):
        return self.scope

    def is_default_scope(self):
        return hasattr(self, 'default_scope') and self.default_scope is not None


class DefaultScope(Scope, AbstractSingleton):
    base_scope = models.OneToOneField(
        Scope,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='default_scope'
    )

    @classmethod
    def load(cls):
        return super(DefaultScope, cls).load()

    @CachedClassProperty
    def instance(cls):
        return cls.load()
