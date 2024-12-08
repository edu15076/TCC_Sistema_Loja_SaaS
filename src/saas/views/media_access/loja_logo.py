from django.urls import reverse

from common.views.mixins import UserInScopeRequiredMixin
from loja.views.media_access import ABCLojaLogoView
from saas.models import ClienteContratante

__all__ = (
    'LojaLogoView',
)


class LojaLogoView(UserInScopeRequiredMixin, ABCLojaLogoView):
    usuario_class = ClienteContratante

    def get_login_url(self):
        return reverse('login_contratacao')
