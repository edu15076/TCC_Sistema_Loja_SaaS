import abc
import os

from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse
from django.views import View

from util.views import ReadImageMixin
from loja.models import Funcionario
from loja.views import UserFromLojaRequiredMixin

__all__ = (
    'ABCLojaLogoView',
    'LojaLogoView',
)


class ABCLojaLogoView(ReadImageMixin, View, abc.ABC):
    def get(self, request, *args, **kwargs):
        logo_path = os.path.join(settings.MEDIA_ROOT, self.user.loja.logo.name)
        if not os.path.exists(logo_path):
            return HttpResponse(status=404)

        try:
            return self.get_img(logo_path)
        except:
            return HttpResponse(status=500)

    @property
    @abc.abstractmethod
    def user(self):
        raise NotImplementedError


class LojaLogoView(UserFromLojaRequiredMixin, ABCLojaLogoView):
    usuario_class = Funcionario

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})
