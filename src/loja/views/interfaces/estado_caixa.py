from abc import ABC, abstractmethod
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from common.views.mixins import UsuarioMixin


class ABCEstadoCaixaCRUDListView(
    ABC, LoginRequiredMixin, UsuarioMixin, ListView
):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Exibe a página com o estado dos caixas de uma loja e permite realizar filtros de exibição.

        :param request: pode conter os seguintes campos de filtro
        - `ordem`: um valor que informa a ordem de exibição.
        - `filtro`: um valor que informa se será exibido os caixas abertos ou fechados.
        - `page`: retorna a respectiva página da listagem.

        :type request: HttpRequest
        :return: Um `context` contendo:
            - `caixas`: lista de caixas da loja.
            - `form`: formulário de cadastro de caixa.
            - `filter_form`: formulário para filtrar caixas.
        :rtype: HttpResponse
        """
        raise NotImplementedError

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações nos caixas (ações de abrir, fechar ou movimentação de dinheiro).

        :param request: deve conter os seguintes campos:
        - `id`: id do caixa a ser alterado.
        - `acao`: ação a ser executada (ex: 'abrir', 'fechar', 'movimentar').

        :type request: HttpRequest
        :return: Resultado da operação.
        :rtype: HttpResponse
        """
        raise NotImplementedError
