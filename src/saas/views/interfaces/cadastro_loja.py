from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView
from django.views.generic.edit import DeletionMixin


class ABCLojaCRUDView(ABC, CreateView, DeletionMixin):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe solicitação para exibir os dados da loja se houver,
        um formulário para cadastro ou atualização e um formulário
        para exclusão se houver loja.

        :return: devolve um `context` com:
        - `loja`
            - `nome`
            - `logo`
        - `form`
        - `delete_form`

        :rtype: HttpResponse
        """

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe um formulário e lida com ele

        :param request: Recebe os valores do formulário:
        - `nome` nome da loja
        - `logo` arquivo da logo
        - `delete` um valor bool, se true, deleta a loja existente

        :type request: HttpRequest

        :return: código 200 indicando sucesso das operações, ou
        outro código indicando falha.
        :rtype: HttpResponse
        """
