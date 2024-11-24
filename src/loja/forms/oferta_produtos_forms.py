from datetime import date
from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from common.models import Periodo
from util.forms import (
    CrispyFormMixin,
    CustomModelMultipleChoiceField,
    CustomModelChoiceField,
)
from loja.models import Produto, Promocao
from loja.validators import validate_unique_promocao


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


class PromocoesPorProdutoForm(CrispyFormMixin, forms.ModelForm):
    promocoes = CustomModelMultipleChoiceField(
        queryset=Promocao.promocoes.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Promoções'),
    )

    class Meta:
        model = Produto
        fields = ['promocoes']

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Salvar')

    def __init__(self, queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        if self.instance and self.instance.pk:
            self.fields['promocoes'].queryset = Promocao.promocoes.filter(
                loja=self.instance.loja,
                data_inicio__gte=date.today(),
            )

    def save(self, commit: bool = True) -> Any:
        instance = super().save(commit=False)
        errors = []

        instance.promocoes.clear()

        for promocao in self.cleaned_data['promocoes']:
            try:
                validate_unique_promocao(instance, promocao)
                instance.promocoes.add(promocao)
            except Exception as e:
                errors.append(str(e))

        if commit:
            instance.save()
            self.save_m2m()

        return (instance, errors)


class DuplicarPromocaoForm(CrispyFormMixin, forms.ModelForm):
    data_inicio = forms.DateField(
        label=_('Data de início'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )
    produtos = CustomModelMultipleChoiceField(
        queryset=Produto.produtos.all(),
        label=_('Produtos'),
        required=False,
    )
    promocao = forms.IntegerField(widget=forms.HiddenInput())

    class Meta:
        model = Promocao
        fields = ['data_inicio', 'produtos']

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Duplicar')

    def __init__(self, loja=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'duplicar_promocao_form'

        if loja:
            produtos_queryset = Produto.produtos.filter(loja=loja)
            self.fields['produtos'].queryset = produtos_queryset

        if kwargs.get('instance'):
            instance = kwargs['instance']
            produtos_queryset = Produto.produtos.filter(loja=instance.loja)
            self.fields['produtos'].queryset = produtos_queryset
            self.fields['produtos'].initial = [instance.produtos]

    def save(self, commit: bool = ...) -> Any:
        instance = Promocao.promocoes.get(pk=self.cleaned_data['promocao'])
        errors = []
        produtos = []

        for produto in self.cleaned_data['produtos']:
            try:
                validate_unique_promocao(produto, instance)
                produtos.append(produto)
            except Exception as e:
                errors.append(str(e))

        replicate = instance
        if commit:
            replicate = instance.clonar_promocao(self.cleaned_data['data_inicio'])
            replicate.produtos.set(produtos)

        return (replicate, errors)


class OfertaProdutosFilterForm(CrispyFormMixin, forms.Form):
    ORDER_CHOICES = [
        ('id', 'Não ordenado'),
        ('-preco_de_venda', 'Menor preço de venda'),
        ('preco_de_venda', 'Maior preço de venda'),
    ]

    STATUS_CHOICES = [('', 'Todos'), (True, 'Em venda'), (False, 'Fora de venda')]

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
        self.helper.form_action = ''
        self.helper.form_id = 'filter_form'
        self.helper.form_class = 'form-inline'
        self.helper.label_class = 'sr-only'
        self.helper.field_class = 'form-control'

    class Meta:
        order_arguments = ['ordem']
        filter_arguments = ['em_venda']
