from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import CreateView


class ABCGerenteLojaCRUDView(ABC, CreateView):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe solicitação para carregar a página e
        envia os dados do gerente, se já houver um
        cadastrado, e o formulário pré-preenchido com
        os dados do gerente já cadastrado.

        :return: um `context` contendo:
        - `gerente_loja` se houver
            - `nome`
            - `sobrenome`
            - `data_nascimento`
            - `email`
            - `telefone`
            - `cpf`
        - `form`

        :rtype: HttpResponse
        """

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe e válida os formulário.

        :param request: deve conter os seguintes campos:
        - `nome`
        - `sobrenome`
        - `data_nascimento`
        - `email`
        - `telefone`
        - `cpf`

        :type request: HttpRequest
        :return: status da operação:
        - `200`: foi cadastrado ou atualizado

        :rtype: HttpResponse
        """
