from django.urls import reverse_lazy

from util.views import CreateHTMXView
from common.forms import (
    UsuarioGenericoPessoaJuridicaAuthenticationForm,
    UsuarioGenericoPessoaJuridicaCreationForm,
    UsuarioGenericoPessoaJuridicaChangeForm,
)
from common.views import (
    LoginUsuarioGenericoView,
    CreateUsuarioGenericoView,
    UpdateUsuarioGenericoView,
    LogoutUsuarioGenericoView,
    PasswordChangeUsuarioGenericoView,
)
from loja.models import Funcionario

__all__ = (
    'LogoutUsuarioLojaView',
    'LoginUsuarioLojaView',
    'CreateUsuarioLojaView',
    'UpdateUsuarioLojaView',
    'PasswordChangeUsuarioLojaView',
)

class PasswordChangeUsuarioLojaView(PasswordChangeUsuarioGenericoView):
    success_url = reverse_lazy('home_loja')
    form_action = reverse_lazy('editar_senha_loja')
    login_url = reverse_lazy('login_loja')
    template_name = 'auth/editar_senha_usuario_loja.html'


class LogoutUsuarioLojaView(LogoutUsuarioGenericoView):
    next_page = reverse_lazy('login_loja')


class LoginUsuarioLojaView(LoginUsuarioGenericoView):
    template_name = 'auth/login_loja.html'
    next_page = reverse_lazy('home_loja')
    authentication_form = UsuarioGenericoPessoaJuridicaAuthenticationForm
    form_action = reverse_lazy('login_loja')


class CreateUsuarioLojaView(CreateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaCreationForm
    template_name = 'auth/criar_usuario_loja.html'
    success_url = reverse_lazy('home_loja')
    form_action = reverse_lazy('criar_usuario_loja')

    # def form_valid(self, form):
    #     return CreateHTMXView.form_valid(self, form)


class UpdateUsuarioLojaView(UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaChangeForm
    template_name = 'auth/editar_usuario_loja.html'
    success_url = reverse_lazy('home_loja')
    login_url = reverse_lazy('login_loja')
    form_action = reverse_lazy('editar_usuario_loja')
    usuario_class = Funcionario
