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
