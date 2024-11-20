from django.contrib.auth.mixins import UserPassesTestMixin

from common.models import (
    UsuarioGenericoPessoa,
    UsuarioGenericoPessoaFisica,
    UsuarioGenericoPessoaJuridica,
)
from scope_auth.models import Scope
from scope_auth.util import get_scope_from_request
from util.decorators import CachedProperty

__all__ = (
    'ScopeMixin',
    'UsuarioMixin',
)


class ScopeMixin:
    @property
    def scope(self) -> Scope:
        return get_scope_from_request(self.request)


class UsuarioMixin:
    usuario_class: type[UsuarioGenericoPessoa] | list[type[UsuarioGenericoPessoa]] = (
        UsuarioGenericoPessoa
    )

    @CachedProperty
    def _usuario_classes(self):
        return (
            self.usuario_class
            if isinstance(self.usuario_class, list)
            else [self.usuario_class]
        ) + [UsuarioGenericoPessoaFisica, UsuarioGenericoPessoaJuridica]

    @property
    def user(self) -> UsuarioGenericoPessoa:
        return UsuarioGenericoPessoa.cast_para_primeira_subclasse(
            self._usuario_classes, self.request.user
        )


class UserInScopeRequiredMixin(ScopeMixin, UsuarioMixin, UserPassesTestMixin):
    def is_user_in_scope(self):
        return self.user.scope == self.scope

    def get_test_func(self):
        return self.is_user_in_scope
