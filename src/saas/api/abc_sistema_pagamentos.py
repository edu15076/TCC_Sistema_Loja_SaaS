from abc import ABC, abstractmethod


class ABCSistemaPagamentosContratos(ABC):
    @classmethod
    @abstractmethod
    def criar_cliente_contratante(cls, cliente_contratante) -> str:
        """Cria um cliente contratante no sistema de pagamentos

        :param cliente_contratante: Cliente contratante a ser criado
        :type cliente_contratante: `saas.models.ClienteContratante`
        :return: String com o código do cliente contratante
        :rtype: str
        """
        pass

    @classmethod
    @abstractmethod
    def criar_metodo_pagameto(cls, token, cartao) -> str:
        """Cria um método de pagamento para um cliente contratante

        :param token: Token do cartão de crédito
        :type token: str
        :param cliente_contratante: Cliente contratante a ser criado
        :type cliente_contratante: `saas.models.ClienteContratante`
        :return: _description_
        :rtype: str
        """
        pass

    @classmethod
    @abstractmethod
    def criar_assinatura(cls, contrato_assinado):
        "receber um possivel código e salvar no contrato assinado"
        pass

    @classmethod
    @abstractmethod
    def trocar_metodo_pagamento_assinatura(cls, cliente_contratante, cartao):
        pass

    @classmethod
    @abstractmethod
    def cancelar_assinatura(cls, cliente_contratante):
        pass

    @classmethod
    @abstractmethod
    def realizar_pagamento(cls, cliente_contratante, pagamento):
        pass
