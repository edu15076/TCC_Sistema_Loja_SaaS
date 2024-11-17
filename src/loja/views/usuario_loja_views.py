from django.urls import reverse_lazy

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
)


__all__ = (
    'LogoutUsuarioLojaView',
    'LoginUsuarioLojaView',
    'CreateUsuarioLojaView',
    'UpdateUsuarioLojaView',
)


class LogoutUsuarioLojaView(LogoutUsuarioGenericoView):
    next_page = reverse_lazy('login_loja')


class LoginUsuarioLojaView(LoginUsuarioGenericoView):
    template_name = 'login.html'
    next_page = reverse_lazy('home_loja')
    authentication_form = UsuarioGenericoPessoaJuridicaAuthenticationForm
    form_action = reverse_lazy('login_loja')


class CreateUsuarioLojaView(CreateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('home_loja')
    form_action = reverse_lazy('criar_usuario_loja')


class UpdateUsuarioLojaView(UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaChangeForm
    template_name = 'change_usuario.html'
    success_url = reverse_lazy('home_loja')
    login_url = reverse_lazy('login_loja')
    form_action = reverse_lazy('editar_usuario_loja')
