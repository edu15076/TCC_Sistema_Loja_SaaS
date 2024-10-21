from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic.edit import UpdateView

from common.models import UsuarioGenericoPessoaJuridica


class ABCContratanteFormView(ABC, UpdateView):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação GET para a página e carrega o formulário vazio,
        se não houver um contratante logado, ou com os dados do contratante.

        :return: uma extrutura HTTP onde o `context` deve conter a chave:
        - `form`: formulário de cadastro

        :rtype: HttpResponse
        """

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """Recebe o formulário preenchido e valida ele

        :param request: Deve receber os seguintes parametros
        - cnpj
        - password
        - email
        - telefone
        - razao_social
        - nome_fantasia

        :type request: HttpRequest
        :return: Uma resposta HTTP com a mensagem de sucesso ou falha.
        :rtype: HttpResponse
        """
        pass
