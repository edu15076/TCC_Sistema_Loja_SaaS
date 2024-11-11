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
    usuario_class: type[UsuarioGenericoPessoa] | list[type[UsuarioGenericoPessoa]] = UsuarioGenericoPessoa

    def get_user(self):
        user = self.request.user
        usuario_classes = self.usuario_class if isinstance(self.usuario_class, list) else [self.usuario_class]
        for usuario_class in usuario_classes:
            try:
                user = usuario_class.from_usuario(user)
            except TypeError:
                continue
            break
        return user
