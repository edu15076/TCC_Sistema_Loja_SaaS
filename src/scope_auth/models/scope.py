from django.db import models
from django.db.models import Q

from util.decorators import CachedClassProperty
from util.models import AbstractSingleton


class ScopeManager(models.Manager):
    def all_but_default(self):
        return self.filter(~Q(id=DefaultScope.instance_id))

    def default_scope(self):
        return DefaultScope.instance.scope


class Scope(models.Model):
    scopes = ScopeManager()

    def is_default_scope(self):
        return hasattr(self, 'default_scope') and self.default_scope is not None


class DefaultScope(Scope, AbstractSingleton):
    scope = models.OneToOneField(
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
