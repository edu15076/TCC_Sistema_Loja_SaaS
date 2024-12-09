from decimal import Decimal

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

from loja.models import (
    Loja,
    Produto,
    Venda
)


class ItemQuerySet(models.QuerySet):
    def annotate_preco_total(self):
        return self.annotate(preco_total=F('quantidade') * F('preco_vendido'))


class ItemManager(models.Manager):
    def get_queryset(self):
        return ItemQuerySet(self.model, using=self._db).all()


class Item(models.Model):
    produto = models.ForeignKey(
        Produto, 
        verbose_name=_('Produto'), 
        on_delete=models.CASCADE
    )
    quantidade = models.PositiveIntegerField(_('Quantidade'), validators=[MinValueValidator(1, _('Quantidade não pode ser nula ou negativa.'))])
    preco_vendido = models.DecimalField(
        _('Preço unitário'),
        max_digits=11,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'), _('Preço não pode ser nulo ou negativo.'))],
    )
    venda = models.ForeignKey(
        Venda,
        verbose_name=_('Venda'),
        related_name='itens',
        on_delete=models.CASCADE
    )
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )

    itens = ItemManager()
    
    @property
    def preco_total(self):
        return self.preco_vendido * self.quantidade
    
    # def clean(self):
    #     if self.caixa.loja != self.produto.loja:
    #         raise ValidationError(
    #             _('O produto não pertence à loja do caixa.')
    #         )
    