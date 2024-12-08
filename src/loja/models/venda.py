from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from loja.validators import validate_data_atual_promocao
from loja.models import (
    Vendedor, 
    Caixeiro,
    Caixa,
    Loja
)


class VendaQuerySet(models.QuerySet):
    pass


class VendaManager(models.Manager):
    def get_queryset(self):
        return VendaQuerySet(self.model, using=self._db).all()
    

class Venda(models.Model):
    vendedor = models.ForeignKey(
        Vendedor, 
        verbose_name=_('Vendedor'), 
        related_name='vendas_como_vendedor',
        on_delete=models.CASCADE
    )
    caixeiro = models.ForeignKey(
        Caixeiro, 
        verbose_name=_('Caixeiro'), 
        related_name='vendas_como_caixeiro',
        on_delete=models.CASCADE
    )
    caixa = models.ForeignKey(
        Caixa, 
        verbose_name=_('Caixa'), 
        on_delete=models.CASCADE
    )
    codigo_nota_fical = models.CharField(_('Código da nota fiscal'), max_length=256, unique=True, null=True, editable=False)
    data_hora = models.DateTimeField(_('Data e hora'), validators=[validate_data_atual_promocao], editable=False, auto_now_add=True)
    porcentagem_desconto = models.DecimalField(_('Porcentagem do desconto'),
        max_digits=5,
        decimal_places=2,
        blank=False,
        validators=[
            MaxValueValidator(100, _('Porcentagem não pode exceder 100%.')),
            MinValueValidator(0, _('Porcentagem não pode ser negativo.')),
        ],
    )
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )

    vendas = VendaManager()
    
    @property
    def preco_total(self):
        return sum([item.preco_total for item in self.itens.all()])
    
    @property
    def desconto(self):
        return self.preco_total * self.porcentagem_desconto / 100
    
    # def clean(self):
    #     if self.caixa.loja != self.produto.loja:
    #         raise ValidationError(
    #             _('O produto não pertence à loja do caixa.')
    #         )