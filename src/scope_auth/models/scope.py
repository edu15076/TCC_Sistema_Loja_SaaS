import functools

from django.db import models
from django.db.models import Q

from util.decorators import CachedClassProperty
from util.models import SingletonMixin
from util.models.singleton import SingletonManager


class ScopeManager(models.Manager):
    def _filter_out_default(self, qs):
        return qs.filter(~Q(pk=DefaultScope.instance_pk))

    def all_but_default(self):
        return self._filter_out_default(self.get_queryset())

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


class DefaultScopeManager(ScopeManager, SingletonManager):
    def get_queryset(self):
        return super().get_queryset().filter(scope=self.default_scope())


class DefaultScope(Scope, SingletonMixin):
    base_scope = models.OneToOneField(
        Scope,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='default_scope',
    )

    @classmethod
    def load(cls):
        return super(DefaultScope, cls).load()

    @CachedClassProperty
    def instance(cls):
        return cls.load()
