from django.urls import reverse_lazy

from common.forms import (
    UsuarioGenericoPessoaJuridicaAuthenticationForm,
    UsuarioGenericoPessoaJuridicaCreationForm,
    UsuarioGenericoPessoaJuridicaChangeForm,
)
from common.views import (LoginUsuarioGenericoView, CreateUsuarioGenericoView,
                          UpdateUsuarioGenericoView, LogoutUsuarioGenericoView,
                          PasswordChangeUsuarioGenericoView)
from saas.forms.usuario_contratacao_forms import ClienteContratanteCreationForm
from saas.models import GerenteDeContratos, ClienteContratante


__all__ = (
    'LogoutUsuarioContratacaoView',
    'LoginUsuarioContratacaoView',
    'CreateUsuarioContratacaoView',
    'UpdateUsuarioContratacaoView',
    'PasswordChangeUsuarioContratacaoView',
)


class PasswordChangeUsuarioContratacaoView(PasswordChangeUsuarioGenericoView):
    success_url = reverse_lazy('home_contratacao')
    form_action = reverse_lazy('editar_senha_contratacao')
    login_url = reverse_lazy('login_contratacao')


class LogoutUsuarioContratacaoView(LogoutUsuarioGenericoView):
    next_page = reverse_lazy('login_contratacao')


class LoginUsuarioContratacaoView(LoginUsuarioGenericoView):
    template_name = 'login.html'
    next_page = reverse_lazy('home_contratacao')
    authentication_form = UsuarioGenericoPessoaJuridicaAuthenticationForm
    form_action = reverse_lazy('login_contratacao')


class CreateUsuarioContratacaoView(CreateUsuarioGenericoView):
    form_class = ClienteContratanteCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('home_contratacao')
    form_action = reverse_lazy('criar_usuario_contratacao')


class UpdateUsuarioContratacaoView(UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaChangeForm
    template_name = 'change_usuario.html'
    success_url = reverse_lazy('home_contratacao')
    login_url = reverse_lazy('login_contratacao')
    form_action = reverse_lazy('editar_usuario_contratacao')
    usuario_class = [GerenteDeContratos, ClienteContratante]
