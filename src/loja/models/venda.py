from datetime import datetime
from decimal import Decimal

from django.db import models
from django.db.models import F, Sum
from django.db.models.functions import Coalesce
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

from loja.models.item import Item
from loja.validators import validate_data_atual_promocao
from loja.models import (
    Vendedor,
    Caixeiro,
    Loja
)


class VendaQuerySet(models.QuerySet):
    def annotate_preco_total(self):
        # TODO: Verificar se tem forma mais extensível de fazer isso
        return self.annotate(
            preco_total=Sum(F('itens__quantidade') * F('itens__preco_vendido'))
        )

    def annotate_preco_total_com_desconto(self):
        return self.annotate_preco_total().annotate(
            preco_total_com_desconto=F('preco_total') * F('porcentagem_desconto') / 100
        )


class VendaManager(models.Manager):
    def get_queryset(self):
        return VendaQuerySet(self.model, using=self._db).all()
    
    def efetuar_venda(
        self, lotes: list[tuple['ProdutoPorLote', int]], valor_pago: Decimal, porcentagem_desconto: Decimal = Decimal('0'), vendedor = None, caixa = None, caixeiro = None
    ):
        quantidade_total, preco_total = 0, 0
        qtd_por_lote = {}

        for lote, qtd in lotes:
            if qtd <= 0:
                raise ValidationError(_('Quantidade deve ser maior que zero.'))
            elif qtd > lote.qtd_em_estoque:
                raise ValidationError(_('Quantidade em estoque insuficiente.'))
            
            qtd_por_lote[lote.pk] = qtd
            quantidade_total += qtd
            preco_total += (lote.produto.preco_de_venda - lote.produto.calcular_desconto()) * qtd
            
            
        produto = lotes[0][0].produto

        if quantidade_total <= 0:
            raise ValidationError(_('Quantidade deve ser maior que zero.'))

        if quantidade_total > produto.qtd_em_estoque:
            raise ValidationError(_('Quantidade em estoque insuficiente.'))
        
        if caixa is None and caixeiro is None:
            raise ValidationError(_('Caixa ou caixeiro não informado.'))
        elif caixa is not None:
            caixeiro = caixa.recuperar_caixeiro(datetime.now())
        elif caixeiro is not None:
            caixa = caixeiro.recuperar_caixa(datetime.now())

        promocao = produto.promocao_ativa()

        itens = []
        for lote, quantidade in lotes:
            item = Item(
                lote=lote,
                quantidade=quantidade,
                preco_vendido=produto.preco_de_venda - produto.calcular_desconto(promocao),
                loja=produto.loja
            )
            itens.append(item)

        if len(itens) == 0:
            raise ValidationError(_('Nenhum item para venda.'))
        
        kwargs = {}
        kwargs['data_hora'] = datetime.now()
        kwargs['loja'] = produto.loja
        kwargs['porcentagem_desconto'] = porcentagem_desconto if porcentagem_desconto is not None else Decimal('0') 
        kwargs['caixa'] = caixa
        kwargs['caixeiro'] = caixeiro

        venda = Venda(**kwargs)

        if preco_total > valor_pago:
            raise ValidationError(_('Valor pago é menor que o valor total da compra.'))

        venda.save()
        caixa.movimentar_dinheiro_em_caixa(float(venda.preco_total))
        for item in itens:
            item.lote.qtd_em_estoque -= item.quantidade
            item.lote.save()
            item.venda = venda
        Item.itens.bulk_create(itens)
        venda.itens.set(itens)


        if vendedor is not None:
            venda.vendedor = vendedor

        venda.save()


        return venda
          


class Venda(models.Model):
    vendedor = models.ForeignKey(
        Vendedor,
        verbose_name=_('Vendedor'),
        related_name='vendas_como_vendedor',
        null=True,
        on_delete=models.CASCADE
    )
    caixeiro = models.ForeignKey(
        Caixeiro,
        verbose_name=_('Caixeiro'),
        related_name='vendas_como_caixeiro',
        on_delete=models.CASCADE
    )
    caixa = models.ForeignKey(
        'loja.Caixa',
        verbose_name=_('Caixa'),
        on_delete=models.CASCADE
    )
    codigo_nota_fical = models.CharField(_('Código da nota fiscal'), max_length=256, unique=True, null=True, editable=False)
    data_hora = models.DateTimeField(_('Data e hora'), validators=[validate_data_atual_promocao], editable=False, auto_now_add=True)
    porcentagem_desconto = models.DecimalField(
        _('Porcentagem do desconto'),
        max_digits=5,
        decimal_places=2,
        blank=False,
        validators=[
            MaxValueValidator(100, _('Porcentagem não pode exceder 100%.')),
            MinValueValidator(0, _('Porcentagem não pode ser negativo.')),
        ],
    )
    comissao_vendedor = models.DecimalField(
        _('Comissão do vendedor'),
        max_digits=11,
        decimal_places=2,
        default=Decimal('0'),
        editable=False
    )
    loja = models.ForeignKey(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )

    vendas = VendaManager()

    @property
    def preco_total(self):
        return self.itens.all().annotate_preco_total().aggregate(
            total=Coalesce(Sum('preco_total'), Decimal('0'))
        )['total']

    @property
    def desconto(self):
        return self.preco_total * self.porcentagem_desconto / 100
    
    def save(self, *args, **kwargs):
        if self.pk is None and hasattr(self, 'vendedor') and self.vendedor:
            self.comissao_vendedor = self.vendedor.porcentagem_comissao         
        return super().save(*args, **kwargs)

    # def clean(self):
    #     if self.caixa.loja != self.produto.loja:
    #         raise ValidationError(
    #             _('O produto não pertence à loja do caixa.')
    #         )
