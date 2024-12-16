from datetime import date, datetime
import json

from crispy_forms.layout import Submit, Layout, MultiWidgetField
from crispy_forms.bootstrap import AppendedText, PrependedText, Field
from crispy_forms.helper import FormHelper
from django import forms
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.db.models import F, ExpressionWrapper, DecimalField

from common.models import Periodo
from util.forms import CrispyFormMixin, CustomModelChoiceField
from util.forms.model_fields import ModelIntegerField
from .mixins import LojaValidatorFormMixin
from util.mixins import NameFormMixin
from loja.models import Loja, Item, Venda, Produto, Vendedor, Caixeiro, Caixa, TrabalhaCaixa, ProdutoPorLote
from loja.validators import validate_unique_promocao


class ProdutoVendaForm(NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'produto_venda'
    should_check_model_form = False

    class Meta:
        model = Produto
        fields = ['codigo_de_barras']
        widgets = {
            'codigo_de_barras': forms.TextInput(attrs={'autofocus': True}),
        }

    def __init__(self, loja=None, *args, **kwargs):
        super().__init__(loja=loja, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Buscar')

    def clean_codigo_de_barras(self):
        codigo_de_barras = self.cleaned_data['codigo_de_barras']
        produto = Produto.produtos.filter(loja=self.loja, codigo_de_barras=codigo_de_barras).first()

        if not produto:
            raise forms.ValidationError(_('Produto não encontrado.'))
        
        self.cleaned_data['codigo_de_barras'] = produto
        return produto
    
    def save(self, commit = ...):
        return self.cleaned_data['codigo_de_barras']


class ItemVendaForm(
    NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm
):
    _name = 'item_venda'
    should_check_model_form = False

    # codigo_de_barras = forms.CharField(
    #     label=_('Código de barras'),
    #     required=True,
    #     max_length=128,
    #     widget=forms.TextInput(attrs={'autofocus': True}),
    # )
    lote_descricao = forms.CharField(
        label=_('Lote:'), required=False, widget=forms.TextInput(attrs={'readonly': True, 'class': 'form-control-plaintext'})
    )
    quantidade = forms.IntegerField(
        label=_('Quantidade'),
        required=True,
        min_value=0,
        initial=0,
        widget=forms.NumberInput(attrs={'autofocus': True}),
        validators=[MinValueValidator(0, _('Quantidade não pode ser negativa.'))],
    )
    lote = ModelIntegerField(
        model_cls=ProdutoPorLote, widget=forms.HiddenInput()
    )

    class Meta:
        model = Item
        fields = ['lote']
        # widgets = {
        #     'quantidade': forms.TextInput(attrs={'autofocus': True}),
        # }

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Salvar')

    def __init__(self, loja=None, lote=None, *args, **kwargs):
        super().__init__(loja=loja, *args, **kwargs)
        if lote:
            self.fields['lote'].initial = lote.pk
        self.helper = self.create_helper(add_submit_button=False)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'lote_descricao',
            'quantidade',
            'lote'
        )
        # self.caixeiro = caixeiro
    
    def save(self, commit = ...):
        # produto = self.cleaned_data['codigo_de_barras']
        quantidade = self.cleaned_data['quantidade']
        if quantidade == 0:
            return None

        lote = self.cleaned_data['lote']
        produto = lote.produto
        preco_vendido = produto.preco_de_venda - produto.calcular_desconto()

        item = Item(
            lote=lote,
            quantidade = quantidade,
            preco_vendido = preco_vendido,
            loja = self.loja
        )


        return item

# TODO Rever lógica do form de venda
class VendaForm(NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'venda'
    should_check_model_form = False

    error_messages = {
        'caixa_nao_encontrado': _('Caixa não encontrado.'),
        'caixa_fechado': _('Caixa fechado.'),
        'compra_vazia': _('Nenhum item adicionado à venda.'),
    }

    itens = forms.CharField(
        widget=forms.HiddenInput()
    )

    vendedor = forms.CharField(
        label=_('Código vendedor'), required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'check-on-blur',
            }
        )
    )

    valor_pago = forms.DecimalField(
        label=_('Valor pago'),
        max_digits=11,
        min_value=0.0,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={
                'autofocus': True,
                'class': 'porcentagem-comissao-input check-on-blur',
            }
        )
    )

    porcentagem_desconto = forms.DecimalField(
        label=_('Desconto'),
        max_digits=5,
        min_value=0.0,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
        })
    )

    class Meta:
        model = Venda
        fields = ['vendedor', 'porcentagem_desconto']

    def __init__(self, loja=None, caixeiro=None, *args, **kwargs):
        super().__init__(loja=loja, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.caixeiro = caixeiro
        self.fields['vendedor'].queryset = Vendedor.vendedores.filter(loja=loja)

        self.helper.form_class = 'form-horizontal'
        self.helper.layout = Layout(
            PrependedText('valor_pago', 'R$', template='efetuar_vendas/fields/field_venda_form.html', field_class='form-group col-md-6'),
            AppendedText('porcentagem_desconto', '%', template='efetuar_vendas/fields/field_venda_form.html', field_class='form-group col-md-6'),
            Field('vendedor', template='efetuar_vendas/fields/field_venda_form.html'),
        )

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Finalizar', css_class='w-100')
    
    def clean_vendedor(self):
        vendedor = self.cleaned_data.get('vendedor')
        if vendedor is None or vendedor == '':
            return None

        return Vendedor.vendedores.filter(loja=self.loja, cpf=vendedor).first()

    def clean_itens(self):
        itens = self.cleaned_data.get('itens')
        try:
            itens_list = json.loads(itens)
            itens_tuples = [
                (
                    ProdutoPorLote.produtos_por_lote.get(pk=item['lote']),
                    item['quantidade'],
                )
                for item in itens_list
            ]
        except (json.JSONDecodeError, KeyError) as e:
            raise forms.ValidationError(_('Formato de itens inválido.'))
        return itens_tuples

    def save(self, commit = ...):
        vendedor = self.cleaned_data.get('vendedor')
        porcentagem_desconto = self.cleaned_data['porcentagem_desconto']

        return Venda.vendas.efetuar_venda(
            self.cleaned_data['itens'],
            self.cleaned_data['valor_pago'],
            vendedor=vendedor,
            caixeiro=self.caixeiro,
            porcentagem_desconto=porcentagem_desconto,
        )

ItensFormSet = forms.formset_factory(
    form=ItemVendaForm,
    extra=0,
    can_delete=False
)

class FormSetHelper(FormHelper):
    def __init__(self, formset_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self._name = formset_name
        submit_button = self.get_submit_button()
        if submit_button:
            self.add_input(submit_button)
        self.render_required_fields = True
        self.create_layout()

    def get_submit_button(self) -> Submit:
        return Submit(self._name + '_submit', _('Salvar'), css_class='w-100')

    def create_layout(self):
        print(self.layout)
        self.layout = Layout(
            MultiWidgetField(
                'lote_descricao',
                'quantidade',
            )
        )
