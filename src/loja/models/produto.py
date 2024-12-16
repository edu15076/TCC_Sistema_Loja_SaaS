from datetime import date, datetime
from decimal import Decimal
from typing import Any

from django.db import models
from django.db.models import F, Sum
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from loja.models.venda import Venda
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
        validators=[MinValueValidator(1, _('Preço não pode ser nulo ou negativo.'))],
    )
    codigo_de_barras = models.CharField(
        _('Código de barras'), max_length=128
    )
    # TODO rever nomenclatura
    em_venda = models.BooleanField(_('À venda'), default=False)
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )

    produtos = ProdutoManager()

    @property
    def qtd_em_estoque(self):
        return sum([lote.qtd_em_estoque for lote in self.lotes.all()])
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save( *args, **kwargs)

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
    
    def atualizar_quantidade_lote(self, codigo_lote: str, quantidade: int):
        lote = self.lotes.get(lote=codigo_lote)

        if lote is None:
            raise ValidationError(f"Lote com código {codigo_lote} não encontrado.")
        
        lote.qtd_em_estoque = quantidade
        lote.save()

    def promocao_valida(self, promocao=None, data: date=date.today()):
        """
        Verifica promoção é válida para período passado.
        """
        try:
            if promocao is None:
                promocao = self.promocao_por_data(data)

            validate_unique_promocao(self, promocao)
            return True
        except ValidationError:
            return False
    
    def calcular_desconto(
        self, promocao = None, data: date = date.today()
    ):
        """
        Calcula o preço de venda do produto para a data passada.
        """
        if promocao is None:
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

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save( *args, **kwargs)
