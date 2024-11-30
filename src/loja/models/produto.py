from datetime import date
from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from loja.validators import validate_unique_promocao
from util.mixins import ValidateModelMixin
from loja.models import Loja

# from .promocao import Promocao


__all__ = ['Produto', 'ProdutoPorLote']


class ProdutoQuerySet(models.QuerySet):
    pass


class ProdutoManager(models.Manager):
    def get_queryset(self):
        return ProdutoQuerySet(self.model, using=self._db).all()

class Produto(ValidateModelMixin, models.Model):
    descricao = models.CharField(_('Descrição'), max_length=246)
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
        return sum([p.qtd_em_estoque for p in self.lotes.filter(produto=self)])

    def promocao_por_data(self, data: date):
        """
        Retorna a promoção ativa para a data passada.
        """

        promocoes = self.promocoes.filter(data_inicio__lte=data)

        promocao_ativa = next(
            (
                promocao
                for promocao in promocoes
                if (data - promocao.data_inicio) < promocao.periodo.tempo_total
            ),
            None,
        )

        return promocao_ativa

    def promocao_ativa(self):
        """
        Retorna a promoção ativa para a data atual.
        """
        return self.promocao_por_data(date.today())

    def promocao_valida(self, data: date):
        """
        Verifica promoção é válida para período passado.
        """
        try:
            validate_unique_promocao(self, self.promocao_por_data(data))
            return True
        except ValidationError:
            return False
    
    def calcular_desconto(
        self, promocao = None, data: date = date.today()
    ):
        """
        Calcula o preço de venda do produto para a data passada.
        """
        if promocao is not None:
            promocao = self.promocao_por_data(data)

        if promocao is not None:
            return Decimal(self.preco_de_venda * promocao.porcentagem_desconto / 100)

        return Decimal(0)


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
