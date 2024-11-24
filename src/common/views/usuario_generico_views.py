from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from common.forms.usuario_generico_forms import (
    UsuarioGenericoCreationForm,
    UsuarioGenericoPessoaJuridicaCreationForm,
    UsuarioGenericoAuthenticationForm,
    UsuarioGenericoPessoaJuridicaAuthenticationForm,
    UsuarioGenericoChangeForm,
    UsuarioGenericoPessoaJuridicaChangeForm,
)
from scope_auth.views import PasswordChangeUserPerScopeWithEmailView
from util.views import CreateHTMXView, UpdateHTMXView, HTMXFormMixin
from .mixins import ScopeMixin, UsuarioMixin, UserInScopeRequiredMixin

__all__ = (
    'CreateUsuarioView',
    'LoginUsuarioView',
    'UpdateUsuarioView',
    'LogoutUsuarioGenericoView',
    'CreateUsuarioGenericoView',
    'LoginUsuarioGenericoView',
    'UpdateUsuarioGenericoView',
    'PasswordChangeUsuarioGenericoView',
)


class PasswordChangeUsuarioGenericoView(
    UserInScopeRequiredMixin, PasswordChangeUserPerScopeWithEmailView
):
    template_name = 'editar_senha.html'


class CreateUsuarioGenericoView(ScopeMixin, CreateHTMXView):
    form_class = UsuarioGenericoCreationForm

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'scope': self.scope}

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginUsuarioGenericoView(ScopeMixin, HTMXFormMixin, LoginView):
    authentication_form = UsuarioGenericoAuthenticationForm

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)


class UpdateUsuarioGenericoView(
    UserInScopeRequiredMixin, UpdateHTMXView
):
    form_class = UsuarioGenericoChangeForm

    def get_object(self, queryset=None):
        return self.user

    def form_invalid(self, form):
        return super().form_invalid(form)


class LogoutUsuarioGenericoView(UserInScopeRequiredMixin, LogoutView):
    next_page = reverse_lazy('login')


class LoginUsuarioView(LoginUsuarioGenericoView):
    template_name = 'login.html'
    next_page = reverse_lazy('home')
    authentication_form = UsuarioGenericoPessoaJuridicaAuthenticationForm
    form_action = reverse_lazy('login')


class CreateUsuarioView(CreateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaCreationForm
    template_name = 'create_user.html'
    success_url = reverse_lazy('home')
    form_action = reverse_lazy('criar_usuario')


class UpdateUsuarioView(UpdateUsuarioGenericoView):
    form_class = UsuarioGenericoPessoaJuridicaChangeForm
    template_name = 'change_usuario.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('login')
    form_action = reverse_lazy('edit_user')
