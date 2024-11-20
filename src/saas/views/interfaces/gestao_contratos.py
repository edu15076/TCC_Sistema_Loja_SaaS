from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from util.views.edit_list import CreateOrUpdateListHTMXView
from common.views.mixins import UsuarioMixin


class ABCGestaoContratoCRUDListView(
    ABC, LoginRequiredMixin, PermissionRequiredMixin, UsuarioMixin, CreateOrUpdateListHTMXView
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
        - `page`: retorna a respectiva pagina.

        :type request: HttpRequest
        :return: um `context` contendo:
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
        - `id`: o id do contrato será ativado ou desativado;

        pode conter os seguintes campos do formulário

        :type request: HttpRequest
        :return: Resultado da operação.
        :rtype: HttpResponse
        """
        return super().post(request, *args, **kwargs)
