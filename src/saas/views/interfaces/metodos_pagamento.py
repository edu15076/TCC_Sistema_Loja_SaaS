from abc import ABC, abstractmethod


from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import DeletionMixin


class ABCMetodosPagamentoCRDView(ABC, ListView, CreateView, DeletionMixin):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação para exibir os métodos de pagamento.

        :param request: Requisição da página com ou sem os seguintes dados
        de filtragem do preenchimento do filter_form:
        -
        :type request: HttpRequest

        :return: um HttpResponse contendo os seguintes dados no `context`:
        - `metodos_pagamento`: lista contendo os métodos de pagamento
            - `padrao`
            - `numero`
            - `codigo`
            - `bandeira`
            - `nome_titular`
        - `form`: formulário para cadastrar novos métodos de pagamento

        :rtype: HttpResponse
        """

    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Pode receber os dados de cadastro de um novo método de pagamento
        ou o método selecionado para ser excluido

        :param request: Dados para cadastro de um novo método de pagamento:
        - `padrao`
        - `numero`
        - `codigo`
        - `bandeira`
        - `nome_titular`
        - `endereco`
            - `cep`
            - `numero`
            - `complemento` opcional

        Ou o `pk` do método a ser deletado em `delete`.
        :type request:

        :return: um HttpResponse informando o status da operação de delete
        ou os valores do novo método de pagamento cadastrado.
        :rtype: HttpResponse
        """
