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

    def __init__(self, scope, queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.fields['promocoes'].queryset = Promocao.promocoes.filter(
            loja__scope=scope,
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

    def __init__(self, scope, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'duplicar_promocao_form'

        produtos_queryset = Produto.produtos.filter(loja__scope=scope)
        self.fields['produtos'].queryset = produtos_queryset

        if kwargs.get('instance'):
            instance = kwargs['instance']
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


class PromocaoForm(CrispyFormMixin, forms.ModelForm):
    numero_de_periodos = forms.IntegerField(
        label=_('Número de períodos'),
        min_value=0,
        error_messages={'min_value': _('Número não pode ser negativo.')},
    )

    unidades_de_tempo_por_periodo = forms.ChoiceField(
        label=_('Unidade de tempo por período'),
        choices=Periodo.UnidadeDeTempo.choices,
        initial=Periodo.UnidadeDeTempo.MES,
    )

    produtos = CustomModelMultipleChoiceField(
        queryset=Produto.produtos.all(),
        label=_('Produtos'),
        required=False,
    )

    class Mata:
        model = Promocao
        fields = ['descricao', 'data_inicio', 'porcentagem_desconto', 'produtos']

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Salvar')
    
    def __init__(self, scope, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.fields['produtos'].queryset = Produto.produtos.filter(loja__scope=scope)

    def save(self, commit = True):
        periodo = Periodo.periodos.create(
            numero_de_periodos=self.cleaned_data.get('numero_de_periodos'),
            unidades_de_tempo_por_periodo=self.cleaned_data.get(
                'unidades_de_tempo_por_periodo'
            ),
        )

        promocao = super().save(commit=False)
        promocao.periodo = periodo

        errors = []
        produtos = []

        for produto in self.cleaned_data['produtos']:
            try:
                validate_unique_promocao(produto, promocao)
                produtos.append(produto)
            except Exception as e:
                errors.append(str(e))

        # * não tenho certeza se vai funcionar
        promocao.produtos.set(produtos)

        if commit:
            promocao.save()
            promocao.produtos.set(produtos)

        return (promocao, errors)
    

class FiltroPromocaoForm(CrispyFormMixin, forms.Form):
    ORDER_CHOICES = [
        ('porcentagem_desconto', _('Menor desconto')),
        ('-porcentagem_desconto', _('Maior desconto')),
        ('id', _("Padrão")),
    ]

    ordem = forms.ChoiceField(label=_('Ordem'), choices=ORDER_CHOICES, required=False)

    STATUS_CHOICES = [
        ('todos', _('Todos')),
        (1, _('Ativas')),
        (2, _('Concluidas')),
        (3, _('Agendadas')),
    ]
    
    produtos = forms.ModelMultipleChoiceField(
        label=_('Produtos presentes'),
        required=False
    )

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Filtrar')

    def __init__(self, scope, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'get'

        self.fields['produtos'].queryset = Promocao.promocoes.filter(loja__scope=scope)

    class Meta:
        order_arguments = ['ordem']
        filter_arguments = {'produtos':'produtos'}

    def full_clean(self):
        super().full_clean()

        status = self.changed_data['status']
        match status:
            case 1:
                self.cleaned_data['status'] = date.today()
                self.Meta.filter_arguments['status'] = 'data_inicio_lte'
            case 2:
                self.cleaned_data['status'] = date.today() # Q('data_inicio') + Q('periodo__numero_de_periodos') * ...
                self.Meta.filter_arguments['status'] = 'data_fim_lte'
            case 3:
                self.cleaned_data['status'] = date.today()
                self.Meta.filter_arguments['status'] = 'data_inicio_gt'

    
