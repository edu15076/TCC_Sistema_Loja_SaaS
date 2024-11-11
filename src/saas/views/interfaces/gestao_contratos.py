from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import DeletionMixin
from django.contrib.auth.mixins import LoginRequiredMixin

from util.views.edit_list import CreateOrUpdateListHTMXView


class ABCGestaoContratoCRUDListView(
    ABC, LoginRequiredMixin, CreateOrUpdateListHTMXView, DeletionMixin
):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe solicitação de carregar a página com os dados de contratos
        de um gerente contratante logado.

        :param request: pode conter os seguintes campos de filtro
        - `ordem`: um valor que informa a ordem de exibição
        - `filtro`: um valor que informa se será exibido os contratos ativos 
            ou inativos
        ? - `query`: talvez tenha como pesquisar pelo possivel titulo de um contrato
        - `page`: retorna a respectiva pagina.

        :type request: HttpRequest
        :return: um `context` contendo:
            // - `usuario`
            - `contratos`:
                - ...
            - `form`: formulário de cadastro de contratos
            - `filter_form`: formulário para filtrar contratos
        :rtype: HttpResponse
        """
        return super().get(request, *args, **kwargs)

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações dos estados dos contratos (criações, deleções
        atualizações)

        :param request: deve conter os seguintes campos:
        //- `action`: informa a ação realizada;

        pode conter os seguintes campos:

        - `id`: o id do contrato será alterado ou excluido;
        - `form`: formulário para criar um contrato;

        :type request: HttpRequest
        :return: Resultado da operação.
        :rtype: HttpResponse
        """
        return super().post(request, *args, **kwargs)