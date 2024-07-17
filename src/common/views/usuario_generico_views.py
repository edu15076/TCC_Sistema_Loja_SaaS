from django.contrib.auth import login
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from common.forms.usuario_generico_forms import UsuarioGenericoCreationForm
from .mixins import ScopeMixin
from util.views import NotLoggedInRequiredMixin, CreateHTMXView

__all__ = (
    'CreateUsuarioView',
    'LoginUsuarioView',
    'CreateUsuarioGenericoView',
    'LoginUsuarioGenericoView'
)


class CreateUsuarioGenericoView(NotLoggedInRequiredMixin, ScopeMixin, CreateHTMXView):
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.get_scope()
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response


class LoginUsuarioGenericoView(NotLoggedInRequiredMixin, ScopeMixin, LoginView):
    pass


class LoginUsuarioView(LoginUsuarioGenericoView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class CreateUsuarioView(CreateUsuarioGenericoView):
    form_class = UsuarioGenericoCreationForm
    template_name = 'create_user.html'
    form_template_name = 'forms/criar_usuario_form.html'
    redirect_url = reverse_lazy('home')
