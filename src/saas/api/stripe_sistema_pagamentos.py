import stripe

from saas.api import ABCSistemaPagamentosContratos
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeSistemaPagamentosContratos(ABCSistemaPagamentosContratos):
    @classmethod
    def criar_cliente_contratante(cls, cliente_contratante) -> str:
        customer = stripe.Customer.create(
            email=cliente_contratante.email,
            name=cliente_contratante.nome_fantasia,
        )
        return customer.id

    @classmethod
    def criar_metodo_pagameto(cls, token, cartao):
        payment_method = stripe.PaymentMethod.create(
            type="card",
            card={
                "token": token,
            },
        )

        # print(payment_method)

        stripe.PaymentMethod.attach(
            payment_method.id,
            customer=cartao.cliente_contratante.customer_id,
        )

        return payment_method

    @classmethod
    def criar_assinatura(cls, contrato_assinado):
        # Implementação para criar assinatura no Stripe
        pass

    @classmethod
    def trocar_metodo_pagamento_assinatura(cls, cartao):
        stripe.Customer.modify(
            cartao.cliente_contratante.customer_id,
            invoice_settings={
                "default_payment_method": cartao.payment_method_id,
            },
        )

    @classmethod
    def cancelar_assinatura(cls, cliente_contratante):
        # Implementação para cancelar assinatura no Stripe
        pass

    def realizar_pagamento(cls, cliente_contratante, pagamento):
        # Implementação para realizar pagamento no Stripe
        pass
