from contextlib import suppress

from common.models import UsuarioGenericoPessoa
from scope_auth.util import get_scope_from_request


__all__ = (
    'ScopeMixin',
    'UsuarioMixin',
)


class ScopeMixin:
    def get_scope(self):
        return get_scope_from_request(self.request)


class UsuarioMixin:
    usuario_class: type(UsuarioGenericoPessoa) = UsuarioGenericoPessoa

    def get_user(self):
        user = self.request.user
        with suppress(TypeError):
            user = self.usuario_class.from_usuario(user)
        return user    