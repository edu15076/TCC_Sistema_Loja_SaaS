from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import DeletionMixin


class ABCPagamentoContratoView(ABC, ListView, CreateView, DeletionMixin):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação para exibir os métodos de pagamento
        e os dados do pagamento

        :param request: Requisição da página
        :type request: HttpRequest

        :return: um HttpResponse contendo os seguintes dados no `context`:
        - `pagamento`: informações sobre o pagamento pendente
            - `valor`
            - `data_inicio_prazo`
            - `data_fim_prazo`
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
        ou o método selecionado para realizar o pagamento ou ser excluido

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

        Ou o `pk` metodo de pagamento selecionado em `metodo_selecionado`
        ou, ainda, o `pk` do método a ser deletado em `delete`.
        :type request:

        :return: um HttpResponse informando o status da operação de pagamento,
        o status da operação de delete ou os valores do novo método de
        pagamento cadastrado.
        :rtype: HttpResponse
        """
