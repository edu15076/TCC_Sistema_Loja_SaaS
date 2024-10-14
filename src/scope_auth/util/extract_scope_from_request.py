from django.http import Http404

from scope_auth.models import Scope


__all__ = ['get_scope_from_request']


def get_scope_from_request(request):
    scope = request.GET.get(
        'scope', request.POST.get(
            'scope', Scope.scopes.default_scope().pk))
    try:
        return Scope.scopes.get(pk=int(scope))
    except (ValueError, Scope.DoesNotExist):
        raise Http404