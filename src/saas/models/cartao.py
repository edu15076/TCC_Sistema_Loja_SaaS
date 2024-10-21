from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist

from common.models import Endereco
from saas.models import ClienteContratante
from util.mixins import ValidateModelMixin, NotUpdatableFieldMixin


class CartaoManager(models.Manager):
    def get_padrao(self, contratante: ClienteContratante = None):
        if contratante is not None:
            objects = self.filter(contratante=contratante)

        return objects.get(padrao=True)

    def realiza_pagamento(self, contratante: ClienteContratante):
        """
        ! ainda não implementado

        realiza pagamento automático no cartão marcado como
        padrão de determinado usuário, se houver mais de um
        ou nenhum levanta excessão. Se não for possivel
        realizar o pagamento, envia um email.
        """

        raise NotImplementedError()

class Cartao(NotUpdatableFieldMixin, ValidateModelMixin, models.Model):
    padrao = models.BooleanField(_('Padrão'), default=False)
    numero = models.PositiveBigIntegerField(_('Numero'))
    codigo = models.PositiveIntegerField(_('Codigo'))
    bandeira = models.PositiveIntegerField(_('Bandeira'), blank=True)
    nome_titular = models.CharField(_('Nome do titular'), max_length=200)

    not_updatable_fields = ['numero', 'codigo', 'bandeira', 'nome_titular']

    contratante = models.ForeignKey(
        ClienteContratante,
        verbose_name=_('Cliente Contratante'),
        on_delete=models.CASCADE,
    )
    
    endereco = models.OneToOneField(
        Endereco, verbose_name=_('Endereço do titular'), on_delete=models.CASCADE
    )

    cartoes = CartaoManager()

    def set_padrao(self):
        try:
            Cartao.cartoes.get_padrao(contratante=self.contratante).update(padrao=False)
            self.padrao = True
            self.save()

        except ObjectDoesNotExist:
            self.padrao = True

    def clean(self):
        if self.padrao:
            self.set_padrao()
