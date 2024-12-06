from abc import ABC, abstractmethod
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from loja.forms.cadastro_caixa_form import CaixaForm
from django.views.generic import ListView
from common.views.mixins import UsuarioMixin
from loja.views.mixins import UserFromLojaRequiredMixin


class ABCGestaoCaixaCRUDListView(
    ABC, UserFromLojaRequiredMixin, UsuarioMixin, ListView
):
    form_class = CaixaForm

    def get_context_data(self, **kwargs):
        """
        formulário e filtros.
        """
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context

    def get_form(self):
        return self.form_class()

    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Exibe a página com os dados dos caixas e permite realizar os filtros.
        """
        pass

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações nos caixas (criação, exclusão, movimentação de dinheiro, etc.).
        """
        pass
