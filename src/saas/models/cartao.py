from typing import Any
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError

from common.models import UsuarioGenericoPessoaJuridica
from common.models import Endereco
from util.logging import Loggers


class CartaoManager(models.Manager):
    def realiza_pagamento(self):
        """
        realiza pagamento automático no cartão marcado como
        padrão de determinado usuário, se houver mais de um
        ou nenhum levanta excessão. Se não for possivel
        realizar o pagamento, envia um email.
        """
        # ! ainda não implementado


class Cartao(models.Model):
    padrao = models.BooleanField(_('Padrão'), default=False)
    numero = models.PositiveBigIntegerField(_('Numero'), editable=False)
    codigo = models.PositiveIntegerField(_('Codigo'), editable=False)
    bandeira = models.PositiveIntegerField(_('Bandeira'), blank=True, editable=False)
    nome_titular = models.CharField(
        _('Nome do titular'), max_length=200, editable=False
    )

    contratante = models.ForeignKey(
        UsuarioGenericoPessoaJuridica,
        verbose_name=_('Cliente Contratante'),
        on_delete=models.CASCADE,
    )
    endereco = models.OneToOneField(
        Endereco, verbose_name=_('Endereço do titular'), on_delete=models.CASCADE
    )

    cartoes = CartaoManager()

    def set_padrao(self):
        try:
            Cartao.objects.filter(contratante=self.contratante, padrao=True).update(
                padrao=False
            )
            self.padrao = True
            self.save()

        except ObjectDoesNotExist:
            self.padrao = True

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        objects = Cartao.objects.filter(contratante=self.contratante)

        if objects.filter(numero=self.numero).exists():
            raise ValidationError(_(
                f'O contratante {self.contratante.nome_fantasia} já'
                'tem um cartão com o número {self.numero}.'
            ))
        if self.padrao and objects.filter(padrao=self.padrao).exists():
            raise ValidationError(_(
                f'Só é permitido um cartão padrão por usuário.'
            ))
