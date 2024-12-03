from datetime import datetime
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator, MinValueValidator

from common.models.periodo import Periodo

from loja.validators import validate_unique_promocao
from util.mixins import ValidateModelMixin, NotUpdatableFieldMixin
from loja.models import Loja
from .produto import Produto

__all__ = ['Promocao']


class PromocaoQuerySet(models.QuerySet):
    pass


class PromocaoManager(models.Manager):
    def get_queryset(self):
        return PromocaoQuerySet(self.model, using=self._db).all()


class Promocao(ValidateModelMixin, models.Model):
    porcentagem_desconto = models.IntegerField(
        _('Porcentagem do desconto'),
        blank=False,
        validators=[
            MaxValueValidator(100, _('Porcentagem não pode exceder 100%.')),
            MinValueValidator(0, _('Porcentagem não pode ser negativo.')),
        ],
    )
    data_inicio = models.DateField(
        _('Data de início'),
        blank=False,
        validators=[
            MinValueValidator(
                datetime.now().date(), _('A data de início não pode ser no passado.')
            )
        ],
    )
    descricao = models.CharField(_('Descrição'), max_length=246, blank=True)
    periodo = models.ForeignKey(
        Periodo, verbose_name=_('Período'), on_delete=models.RESTRICT
    )
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )
    produtos = models.ManyToManyField(
        Produto,
        verbose_name=_('Produtos'),
        related_name='promocoes',
        default=None,
    )

    promocoes = PromocaoManager()

    def clean(self) -> None:
        super().clean()

        if self.pk is None or self.produtos is None:
            return

        for produto in self.produtos.all():
            validate_unique_promocao(produto, self)

    def clonar_promocao(self, data_inicio: datetime, commit=True) -> 'Promocao':
        """
        Clona a promoção atual com a data de início passada.
        """
        promocao = Promocao(
            porcentagem_desconto=self.porcentagem_desconto,
            data_inicio=data_inicio,
            descricao=self.descricao,
            periodo=self.periodo,
            loja=self.loja,
        )

        if commit:
            promocao.save()
            
        return promocao
