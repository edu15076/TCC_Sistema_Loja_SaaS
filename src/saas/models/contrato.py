from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinLengthValidator

from common.models.periodo import Periodo


__all__ = [
    'ContratoQuerySet',
    'ContratoManager',
    'Contrato'
]


class ContratoQuerySet(models.QuerySet):
    pass


class ContratoManager(models.Manager):
    def get_queryset(self):
        return ContratoQuerySet(self.model, using=self._db).all()


class Contrato(models.Model):
    descricao = models.CharField(_('Descrição'), max_length=512, blank=True)
    ativo = models.BooleanField(_('Ativo'), default=False)
    valor_por_periodo = models.DecimalField(_('Valor por perido'), max_digits=11, decimal_places=2)
    telas_simultaneas = models.IntegerField(_('Telas simulteneas'), null=True)
    taxa_de_multa = models.IntegerField(_('Taxa de multa'), blank=False, validators=[
        MaxLengthValidator(100, _('Porcentagem não pode exceder 100%.')),
        MinLengthValidator(0, _('Porcentagem não pode ser negativo.'))
    ])
    tempo_maximo_de_atraso_em_dias = models.IntegerField(
        _('Tempo máximo de atraso em dias'), 
        validators=MinLengthValidator(0, _('Tempo não pode ser negativo.'))
    )
    periodo = models.ForeignKey(Periodo, on_delete=models.RESTRICT)

    contratos = ContratoManager()

    @property
    def valor_total(self):
        return self.valor_por_periodo * self.periodo.numero_de_periodos
    
