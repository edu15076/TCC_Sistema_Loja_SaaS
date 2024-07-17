from scope_auth.util import get_scope_from_request


__all__ = (
    'ScopeMixin',
)


class ScopeMixin:
    def get_scope(self):
        return get_scope_from_request(self.request)

