from datetime import timedelta

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator


__all__ = [
    'Periodo'
]


class Periodo(models.Model):
    class UnidadeDeTempo(models.TextChoices):
        ANO = "ANO", _('Ano')
        MES = "MES", _("Mes")
        DIA = "DIA", _("Dia")

    numero_de_periodos = models.IntegerField(
        _('Numero de periodos'),
        validators=[MinValueValidator(0, _('Numero de  não pode ser negativo.'))]
    )
    unidades_de_tempo_por_periodo = models.CharField(
        _('Unidade de tempo por periodo'), 
        max_length=3,
        choices=UnidadeDeTempo,
        default=UnidadeDeTempo.MES
    )

    periodos = models.Manager()

    @property
    def tempo_total(self):
        if self.unidades_de_tempo_por_periodo == self.UnidadeDeTempo.DIA:
            return timedelta(days=self.numero_de_periodos)
        elif self.unidades_de_tempo_por_periodo == self.UnidadeDeTempo.MES:
            return timedelta(days=30 * self.numero_de_periodos)
        else:
            return timedelta(days=365 * self.numero_de_periodos)
