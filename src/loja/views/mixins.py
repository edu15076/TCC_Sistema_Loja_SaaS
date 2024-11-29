from typing import Any

from django.db.models.query import QuerySet
from common.views.mixins import UserInScopeRequiredMixin
from scope_auth.models import Scope

__all__ = (
    'UserFromLojaRequiredMixin',
)


class UserFromLojaRequiredMixin(UserInScopeRequiredMixin):
    """
    Classe que além de validar se o usuário está logado e está acessando o escopo
    correto, também verifica se o escopo não é de contratação
    """
    def is_user_in_scope(self) -> bool:
        return (
                super().is_user_in_scope()
                and self.scope != Scope.scopes.default_scope()
                and hasattr(user := self.user, 'loja')
                and user.loja.contratante.is_signing_contract()
        )
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(loja__scope=self.scope)
    
    def get_object(self, queryset: QuerySet[Any] | None = None):
        object = super().get_object(queryset)

        if object is not None and object.loja.scope != self.scope:
            return None

        return object
