from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.generic import TemplateView
from django.core.exceptions import PermissionDenied

from common.views.mixins import UserInScopeRequiredMixin
from loja.models import Loja
from saas.models import ClienteContratante, GerenteDeContratos

__all__ = (
    'HomeContratacao',
)


class HomeContratacao(UserInScopeRequiredMixin, TemplateView):
    template_name = 'home_contratacao.html'

    bypass_unauthenticated_user = True
    usuario_class = [GerenteDeContratos, ClienteContratante]

    def handle_no_permission(self):
        try:
            loja_pk: int = Loja.lojas.get(scope=self.user.scope).pk
            return HttpResponseRedirect(
                reverse('home_loja', kwargs={'loja_scope': loja_pk})
            )
        except Loja.DoesNotExist:
            raise PermissionDenied(self.get_permission_denied_message())
