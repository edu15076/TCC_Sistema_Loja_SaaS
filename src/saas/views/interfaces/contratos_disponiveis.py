from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import FormView

from util.views import MultipleObjectFilterMixin
from common.views.mixins import UsuarioMixin


class ABCContratosDisponiveisCRUDView(
    ABC, FormView, MultipleObjectFilterMixin, UsuarioMixin
):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação para carregar o formulário

        :return: um `context` com o formulário em `form`
        :rtype: HttpResponse
        """

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe um formulário de solicitação de suporte
        por `POST` e envia para o email de suporte
        apropriado.

        :param request: contém os seguintes campos do
        formulário preenchido:
        - `assunto` pode ser:
            - `loja`
            - `contratos`
            - `falha`
        - `motivo` uma frase curta contendo o motivo
        - `descrição` uma descrição textual mais longa
        explicando o que aconteceu

        :type request: HttpRequest

        :return: Retorna o status da solicitação de contato,
        200 se foi possivel contactar
        :rtype: HttpResponse
        """
