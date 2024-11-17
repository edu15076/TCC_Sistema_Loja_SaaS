from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

from util.views import HTMXFormMixin
from .forms import PasswordChangeUserPerScopeWithEmailForm


class PasswordChangeUserPerScopeWithEmailView(
    LoginRequiredMixin, PasswordChangeView, HTMXFormMixin
):
    form_class = PasswordChangeUserPerScopeWithEmailForm
    success_url = reverse_lazy('home')
    form_action = reverse_lazy('change_password')
    login_url = reverse_lazy('login')

    def form_valid(self, form):
        PasswordChangeView.form_valid(self, form)
        return HTMXFormMixin.form_valid(self, form)
