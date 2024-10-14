from scope_auth.models import Scope, ScopeManager, DefaultScope


__all__ = (
    'LojaScopeManager',
    'LojaScope',
    'ContratosScope'
)


class LojaScopeManager(ScopeManager):
    def get_queryset(self):
        return self._filter_out_default(super().get_queryset())

    def from_scopes_queryset(self, qs):
        qs.__class__ = LojaScope
        qs.model = LojaScope
        return qs


class LojaScope(Scope):
    scopes = LojaScopeManager()

    @classmethod
    def from_scope(cls, scope):
        scope.__class__ = LojaScope
        return scope

    class Meta:
        proxy = True


class ContratosScope(DefaultScope):
    @classmethod
    def from_scope(cls, scope):
        scope.__class__ = ContratosScope
        return scope

    class Meta:
        proxy = True
