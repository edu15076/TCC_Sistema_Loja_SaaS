from django.urls import reverse
from django.views.generic import TemplateView

from loja.models import Funcionario
from loja.views.mixins import UserFromLojaRequiredMixin

__all__ = (
    'HomeLojaView',
)


class HomeLojaView(UserFromLojaRequiredMixin, TemplateView):
    template_name = 'home_loja.html'
    usuario_class = Funcionario

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})
