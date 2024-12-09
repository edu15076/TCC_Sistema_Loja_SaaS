from datetime import date, datetime
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import F, ExpressionWrapper, DecimalField

from common.models import Periodo
from util.forms import CrispyFormMixin, CustomModelChoiceField
from util.forms.model_fields import ModelIntegerField
from .mixins import LojaValidatorFormMixin
from util.mixins import NameFormMixin
from loja.models import Loja, Item, Venda, Produto, Vendedor, Caixeiro, Caixa, TrabalhaCaixa
from loja.validators import validate_unique_promocao


class ItemVendaForm(
    NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm
):
    _name = 'item_venda'
    should_check_model_form = False

    codigo_de_barras = forms.CharField(
        label=_('Código de barras'),
        required=True,
        max_length=128,
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
    # quantidade = forms.IntegerField(_('Quantidade'), min_value=1, initial=1)

    class Meta:
        model = Item
        fields = ['codigo_de_barras', 'quantidade']

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Salvar')

    def __init__(self, loja=None, caixeiro=None, *args, **kwargs):
        print(loja)
        super().__init__(loja=loja, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.caixeiro = caixeiro

    def clean_codigo_de_barras(self):
        codigo_de_barras = self.cleaned_data['codigo_de_barras']
        produto = Produto.produtos.filter(loja=self.loja, codigo_de_barras=codigo_de_barras).first()

        if not produto:
            raise forms.ValidationError(_('Produto não encontrado.'))
        
        self.cleaned_data['codigo_de_barras'] = produto
        return produto
    
    def save(self, commit = ...):
        produto = self.cleaned_data['codigo_de_barras']
        quantidade = self.cleaned_data['quantidade']
        preco_vendido = produto.preco_de_venda - produto.calcular_desconto()

        print(self.loja)
        item = Item(
            produto = produto,
            quantidade = quantidade,
            preco_vendido = preco_vendido,
            loja = self.loja
        )

        return item


class VendaForm(NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'venda'
    should_check_model_form = True

    error_messages = {
        'caixa_nao_encontrado': _('Caixa não encontrado.'),
        'caixa_fechado': _('Caixa fechado.'),
        'compra_vazia': _('Nenhum item adicionado à venda.'),
    }

    vendedor = CustomModelChoiceField(
        label=_('Vendedor'), required=False, queryset=Vendedor.vendedores.all(), empty_label=None
    )

    caixa = ModelIntegerField(label=_('Caixa'), model_cls=Caixa, min_value=1)

    class Meta:
        model = Venda
        fields = ['vendedor', 'porcentagem_desconto']

    def __init__(self, loja=None, caixeiro=None, *args, **kwargs):
        super().__init__(loja=loja, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.caixeiro = caixeiro
        self.fields['vendedor'].queryset = Vendedor.vendedores.filter(loja=loja)

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Finalizar')

    def clean_caixa(self):
        caixa = self.cleaned_data['caixa']

        if not caixa:
            raise forms.ValidationError(self.error_messages['caixa_nao_encontrado'])
        if not caixa.is_open:
            raise forms.ValidationError(self.error_messages['caixa_fechado'])
        
        return caixa
        
    def clean_itens(self):
        itens = self.cleaned_data['itens']
        """
        itens = [
            codigo_de_barras,
            quantidade,
        ]
        """

        if not itens:
            raise forms.ValidationError(self.error_messages['compra_vazia'])

        itens_cleaned = [ItemVendaForm(loja=self.loja, data=item).save() for item in itens]
        
        self.cleaned_data['itens'] = itens_cleaned
        return itens_cleaned

    def save(self, commit = ...):
        vendedor = self.cleaned_data.get('vendedor')
        # caixa = self.cleaned_data['caixa']
        caixeiro = self.caixeiro
        porcentagem_desconto = self.cleaned_data['porcentagem_desconto']
        caixa = caixeiro.recuperar_caixa(datetime.now())
        print(caixa)

        self.cleaned_data['loja'] = self.loja

        if commit:
            venda = Venda(
                vendedor=vendedor,
                # caixa=caixa,
                porcentagem_desconto=porcentagem_desconto,
                loja=self.loja,
                caixeiro=caixeiro
            )
            venda.save()
            venda.itens.set(self.cleaned_data['itens'])

        venda = super().save(commit=False)
        venda.loja = self.loja
        venda.save()
        return venda


# class PagamentoVendaForm(NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
#     _name = 'pagamento_venda'
#     should_check_model_form = False
#     fields_loja_check = ['venda']

#     valor_pago = forms.DecimalField(
#         label=_('Valor pago'),
#         max_digits=11,
#         min_value=0.0,
#         decimal_places=2,
#         widget=forms.NumberInput(attrs={'autofocus': True}),
#     )
#     venda = ModelIntegerField(
#         label=_('Venda'), model_cls=Venda, min_value=1, widget=forms.HiddenInput()
#     )

#     def __init__(self, loja=None, *args, **kwargs):
#         super().__init__(loja=loja, *args, **kwargs)
#         self.helper = self.create_helper()
#         self.helper.form_method = 'post'

#     def get_submit_button(self) -> Submit:
#         return Submit(self.submit_name(), 'Finalizar')

#     def clean_valor_pago(self):
#         valor_pago = self.cleaned_data['valor_pago']
#         venda = self.instance

#         if valor_pago < venda.preco_total:
#             raise forms.ValidationError(_('Valor pago é menor que o valor total da compra.'))

#         return valor_pago
