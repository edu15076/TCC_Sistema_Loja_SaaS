from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin

from common.models import (
    UsuarioGenericoPessoa,
    UsuarioGenericoPessoaFisica,
    UsuarioGenericoPessoaJuridica,
)
from scope_auth.models import Scope
from scope_auth.util import get_scope_from_request
from util.decorators import CachedProperty, CachedClassProperty

__all__ = (
    'ScopeMixin',
    'UsuarioMixin',
    'UserInScopeRequiredMixin',
)


class ScopeMixin:
    @property
    def scope(self) -> Scope | None:
        if not hasattr(self, 'request'):
            return None
        return get_scope_from_request(self.request)


class UsuarioMixin:
    usuario_class: type[UsuarioGenericoPessoa] | list[type[UsuarioGenericoPessoa]] = []

    @CachedClassProperty
    def _usuario_classes(cls):
        return (
            cls.usuario_class
            if isinstance(cls.usuario_class, list)
            else [cls.usuario_class]
        ) + [UsuarioGenericoPessoaFisica, UsuarioGenericoPessoaJuridica]

    @CachedProperty
    def user(self) -> UsuarioGenericoPessoa:
        return UsuarioGenericoPessoa.cast_para_primeira_subclasse(
            self._usuario_classes, self.request.user
        )


class UserInScopeRequiredMixin(
    UsuarioMixin, ScopeMixin, LoginRequiredMixin, UserPassesTestMixin
):
    """Classe que valida se o usuário está logado e está acessando o escopo correto"""
    def is_user_in_scope(self) -> bool:
        return self.user.scope == self.scope

    def get_test_func(self):
        return self.is_user_in_scope
