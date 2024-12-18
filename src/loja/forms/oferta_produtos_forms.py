from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from util.forms import CrispyFormMixin
from .mixins import LojaValidatorFormMixin
from loja.models import Produto

# TODO - Refatorar para usar LojaValidatorFormMixin e ModelFields

class ProdutoEmVendaForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['em_venda']

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Salvar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'


class PrecoDeVendaProdutoForm(CrispyFormMixin, forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['preco_de_venda']

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Salvar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'


class OfertaProdutosFilterForm(CrispyFormMixin, forms.Form):
    ORDER_CHOICES = [
        ('id', 'Não ordenado'),
        ('-preco_de_venda', 'Menor preço de venda'),
        ('preco_de_venda', 'Maior preço de venda'),
    ]

    STATUS_CHOICES = [('', 'Todos'), (True, 'À venda'), (False, 'Fora de venda')]

    ordem = forms.ChoiceField(
        label=_('Ordenar por'),
        choices=ORDER_CHOICES,
        required=False,
    )

    em_venda = forms.ChoiceField(
        label=_('Status'),
        choices=STATUS_CHOICES,
        required=False,
    )

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Filtrar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'get'
        self.helper.form_id = 'filter_form'

    class Meta:
        order_arguments = ['ordem']
        filter_arguments = ['em_venda']
