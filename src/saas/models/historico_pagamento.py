from django.db import models
from django.utils.translation import gettext_lazy as _

from saas.models.contrato_assinado import ContratoAssinado
from saas.models.usuario_contratacao import ClienteContratante

__all__ = [
    'HistoricoPagamentosQuerySet',
    'HistoricoPagamentosManager',
    'HistoricoPagamentos',
]

class HistoricoPagamentosQuerySet(models.QuerySet):
    pass


class HistoricoPagamentosManager(models.Manager):
    def get_queryset(self):
        return HistoricoPagamentosQuerySet(self.model, using==self._db).all()
    

class HistoricoPagamentos(models.Model):
    valor_a_ser_pago = models.DecimalField(_('Valor a ser pago'), max_digits=11, decimal_places=2)
    data_pagamento = models.DateField(_('Data do pagamento'), auto_now=False, auto_now_add=False)
    data_inicio_prazo_pagamento = models.DateField(_('Data de inicio do pagamento'), auto_now=False, auto_now_add=False)
    data_fim_prazo_pagamento = models.DateField(_('Data final do pagamento'), auto_now=False, auto_now_add=False)

    contrato_assinado = models.ForeignKey(ContratoAssinado, on_delete=models.RESTRICT)

    historicos = HistoricoPagamentosManager()