from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from saas.api import StripeSistemaPagamentosContratos as payment_api
from common.models import Endereco
from saas.models import ClienteContratante
from util.mixins import ValidateModelMixin, NotUpdatableFieldMixin


class CartaoQuerySet(models.QuerySet):
    pass

class CartaoManager(models.Manager):
    def get_queryset(self):
        return CartaoQuerySet(self.model, using=self._db).all()

    def get_padrao(self, cliente_contratante: ClienteContratante = None):
        if cliente_contratante is not None:
            objects = self.filter(cliente_contratante=cliente_contratante)

        return objects.get(padrao=True)

    def realiza_pagamento(self, cliente_contratante: ClienteContratante):
        """
        ! ainda não implementado

        realiza pagamento automático no cartão marcado como
        padrão de determinado usuário, se houver mais de um
        ou nenhum levanta excessão. Se não for possivel
        realizar o pagamento, envia um email.
        """

        raise NotImplementedError()


class Cartao(NotUpdatableFieldMixin, models.Model):
    class Bandeiras(models.IntegerChoices):
        VISA = 4, _('Visa')
        MASTERCARD = 2, _('Mastercard')

    payment_method_id = models.CharField(_('ID do pagamento'), max_length=248, unique=True)
    bandeira = models.IntegerField(_('Bandeira'), choices=Bandeiras)
    mes_validade = models.PositiveSmallIntegerField(_('Mês de validade'))
    ano_validade = models.PositiveSmallIntegerField(_('Ano de validade'))
    nome_titular = models.CharField(_('Nome do titular'), max_length=200)
    numero = models.CharField(_('Numero'), max_length=4)
    padrao = models.BooleanField(_('Padrão'), default=False)
    cliente_contratante = models.ForeignKey(
        ClienteContratante,
        verbose_name=_('Cliente Contratante'),
        on_delete=models.CASCADE,
    )
    endereco = models.OneToOneField(
        Endereco, verbose_name=_('Endereço do titular'), on_delete=models.CASCADE
    )

    # not_updatable_fields = ['numero', 'codigo', 'bandeira', 'nome_titular']

    @property
    def token(self) -> str:
        return self._token
    
    @token.setter
    def token(self, value: str):
        self._token = value


    cartoes = CartaoManager()

    @classmethod
    def get_bandeira(cls, bandeira_str):
        for bandeira in cls.Bandeiras.choices:
            if bandeira_str.lower() == bandeira[1].lower():
                return bandeira[0]
        return None


    def set_padrao(self):
        try:
            Cartao.cartoes.filter(cliente_contratante=self.cliente_contratante).update(padrao=False)
            self.padrao = True
            payment_api.trocar_metodo_pagamento_assinatura(self)
            self.save()

        except ObjectDoesNotExist:
            self.padrao = True

    # def clean(self):
    #     if self.padrao:
    #         self.set_padrao()

    def save(self, *args, **kwargs):
        print(len(self.payment_method_id) == 0)
        if len(self.payment_method_id) == 0:
            print('aaaaaaaaaaa')
            payment_method = payment_api.criar_metodo_pagameto(self.token, self)
            self.payment_method_id = payment_method.id
            self.numero = payment_method.card.last4
            self.ano_validade = payment_method.card.exp_year
            self.mes_validade = payment_method.card.exp_month
            self.bandeira = self.get_bandeira(payment_method.card.brand)

            if self.padrao or Cartao.cartoes.filter(cliente_contratante=self.cliente_contratante).count() == 0:
                self.set_padrao()


        self.full_clean()

        super().save(*args, **kwargs)


