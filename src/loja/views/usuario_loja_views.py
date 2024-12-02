from django.contrib.auth import logout
from django.urls import reverse

from common.forms import (
    UsuarioGenericoPessoaFisicaAuthenticationForm,
    UsuarioGenericoPessoaFisicaCreationForm,
    UsuarioGenericoPessoaFisicaChangeForm,
)
from common.views import (
    LoginUsuarioGenericoView,
    CreateUsuarioGenericoView,
    UpdateUsuarioGenericoView,
    LogoutUsuarioGenericoView,
    PasswordChangeUsuarioGenericoView,
)
from common.views.mixins import ScopeMixin
from loja.models import Funcionario
from .mixins import UserFromLojaRequiredMixin

__all__ = (
    'LogoutUsuarioLojaView',
    'LoginUsuarioLojaView',
    'UpdateUsuarioLojaView',
    'PasswordChangeUsuarioLojaView',
)


class PasswordChangeUsuarioLojaView(
    UserFromLojaRequiredMixin, PasswordChangeUsuarioGenericoView
):
    template_name = 'auth/editar_senha_usuario_loja.html'
    usuario_class = Funcionario

    @property
    def success_url(self):
        return reverse('home_loja', kwargs={'loja_scope': int(self.scope)})

    @property
    def form_action(self):
        return reverse('editar_senha_loja', kwargs={'loja_scope': int(self.scope)})

    @property
    def login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class LogoutUsuarioLojaView(LogoutUsuarioGenericoView, ScopeMixin):
    @property
    def next_page(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class LoginUsuarioLojaView(LoginUsuarioGenericoView):
    template_name = 'auth/login_loja.html'
    authentication_form = UsuarioGenericoPessoaFisicaAuthenticationForm

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if not hasattr(request.user, 'funcionario_loja'):
            logout(request)
        return response

    @property
    def form_action(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    @property
    def next_page(self):
        return reverse('home_loja', kwargs={'loja_scope': int(self.scope)})


class UpdateUsuarioLojaView(UserFromLojaRequiredMixin, UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaFisicaChangeForm
    template_name = 'auth/editar_usuario_loja.html'
    usuario_class = Funcionario

    @property
    def success_url(self):
        return reverse('home_loja', kwargs={'loja_scope': int(self.scope)})

    @property
    def login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    @property
    def form_action(self):
        return reverse('editar_usuario_loja', kwargs={'loja_scope': int(self.scope)})
