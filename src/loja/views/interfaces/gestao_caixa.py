from abc import ABC, abstractmethod
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from util.views.edit_list import CreateOrUpdateListHTMXView
from common.views.mixins import UsuarioMixin


class ABCGestaoCaixaCRUDListView(
    ABC, LoginRequiredMixin, UsuarioMixin, CreateOrUpdateListHTMXView
):
    """
    Interface para gestão de caixa, com operações de abrir, fechar e movimentar dinheiro no caixa.
    """

    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Exibe a página com os dados dos caixas de uma loja e permite realizar filtros de exibição.

        :param request: pode conter os seguintes campos de filtro
        - `ordem`: um valor que informa a ordem de exibição.
        - `filtro`: um valor que informa se será exibido os caixas ativos ou inativos.
        - `page`: retorna a respectiva página da listagem.

        :type request: HttpRequest
        :return: Um `context` contendo:
            - `caixas`: lista de caixas da loja.
            - `form`: formulário de cadastro de caixa.
            - `filter_form`: formulário para filtrar caixas.
        :rtype: HttpResponse
        """
        return super().get(request, *args, **kwargs)

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações nos caixas (criação, exclusão, movimentação de dinheiro, fechamento).

        :param request: deve conter os seguintes campos:
        - `id`: id do caixa a ser alterado.
        - `acao`: ação a ser executada (ex: 'abrir', 'fechar', 'movimentar').

        :type request: HttpRequest
        :return: Resultado da operação.
        :rtype: HttpResponse
        """
        return super().post(request, *args, **kwargs)