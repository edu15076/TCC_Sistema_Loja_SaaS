from datetime import datetime

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator

from util.mixins import ValidateModelMixin
from loja.models import Loja, Promocao


__all__ = ['Produto', 'ProdutoPorLote']


class ProdutoQuerySet(models.QuerySet):
    pass


class ProdutoManager(models.Manager):
    def get_queryset(self):
        return ProdutoQuerySet(self.model, using=self._db).all()


class Produto(ValidateModelMixin, models.Model):
    preco_de_venda = models.DecimalField(
        _('Preço de venda'),
        max_digits=11,
        decimal_places=2,
        validators=[MinValueValidator(0, _('Preço não pode ser negativo.'))],
    )
    codigo_de_barras = models.CharField(
        _('Código de barras'), max_length=128, blank=True
    )
    em_venda = models.BooleanField(_('Disponível para venda'), default=False)
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.RESTRICT, editable=False
    )

    produtos = ProdutoManager()

    @property
    def qtd_em_estoque(self):
        return sum(
            [
                p.qtd_em_estoque
                for p in self.lotes.produtos_por_lote.filter(produto=self)
            ]
        )

    def promocao_por_data(self, data: datetime) -> 'Promocao' | None:
        """
        Retorna a promoção ativa para a data passada.
        """

        promocao = (
            self.promocoes.filter(data_inicio__lte=data)
            .annotate(tempo_total=F('periodo__tempo_total'))
            .filter(tempo_total__gte=(data - F('data_inicio')))
            .first()
        )

        return promocao if promocao else None

    def promocao_ativa(self) -> 'Promocao' | None:
        """
        Retorna a promoção ativa para a data atual.
        """
        return self.promocao_por_data(datetime.now())


class ProdutoPorLoteQuerySet(models.QuerySet):
    pass


class ProdutoPorLoteManager(models.Manager):
    def get_queryset(self):
        return ProdutoPorLoteQuerySet(self.model, using=self._db).all()


class ProdutoPorLote(models.Model):
    lote = models.CharField(_('Lote'), max_length=128)
    qtd_em_estoque = models.IntegerField(
        _('Quantidade'),
        validators=[MinValueValidator(0, _('Quantidade não pode ser negativo.'))],
    )
    produto = models.ForeignKey(
        Produto,
        verbose_name=_('Produto'),
        on_delete=models.RESTRICT,
        editable=False,
        related_name='lotes',
    )

    produtos_por_lote = ProdutoPorLoteManager()
