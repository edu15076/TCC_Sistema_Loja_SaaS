from scope_auth.util import get_scope_from_request


def current_scope(request):
    return {'scope': get_scope_from_request(request)}
