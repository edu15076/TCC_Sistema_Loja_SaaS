from django.urls import reverse_lazy

from common.forms import (
    UsuarioGenericoPessoaJuridicaAuthenticationForm,
    UsuarioGenericoPessoaJuridicaCreationForm,
    UsuarioGenericoPessoaJuridicaChangeForm
)
from common.views import (LoginUsuarioGenericoView, CreateUsuarioGenericoView,
                          UpdateUsuarioGenericoView, LogoutUsuarioGenericoView)


__all__ = (
    'LogoutUsuarioContratacaoView',
    'LoginUsuarioContratacaoView',
    'CreateUsuarioContratacaoView',
    'UpdateUsuarioContratacaoView'
)


class LogoutUsuarioContratacaoView(LogoutUsuarioGenericoView):
    next_page = reverse_lazy('login_contratacao')


class LoginUsuarioContratacaoView(LoginUsuarioGenericoView):
    template_name = 'login.html'
    next_page = reverse_lazy('home_contratacao')
    authentication_form = UsuarioGenericoPessoaJuridicaAuthenticationForm
    form_action = reverse_lazy('login_contratacao')


class CreateUsuarioContratacaoView(CreateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('home_contratacao')
    form_action = reverse_lazy('criar_usuario_contratacao')


class UpdateUsuarioContratacaoView(UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaChangeForm
    template_name = 'change_usuario.html'
    success_url = reverse_lazy('home_contratacao')
    login_url = reverse_lazy('login_contratacao')
    form_action = reverse_lazy('editar_usuario_contratacao')
