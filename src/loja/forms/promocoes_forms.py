from datetime import date
from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _
from django.db.models import F, ExpressionWrapper, DecimalField

from common.models import Periodo
from loja.models.loja import Loja
from util.forms import (
    CrispyFormMixin,
    CustomModelMultipleChoiceField
)
from .mixins import LojaValidatorFormMixin
from util.mixins import NameFormMixin
from loja.models import Produto, Promocao
from loja.validators import validate_unique_promocao

# TODO - Refatorar para usar LojaValidatorFormMixin e ModelFields

class PromocoesPorProdutoForm(NameFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'promocoes_por_produto'

    promocoes = CustomModelMultipleChoiceField(
        queryset=Promocao.promocoes.all(),
        widget=forms.CheckboxSelectMultiple,
        label=_('Promoções'),
    )

    class Meta:
        model = Produto
        fields = ['promocoes']

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Salvar')

    def __init__(self, scope, queryset=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.fields['promocoes'].queryset = Promocao.promocoes.filter(
            loja__scope=scope,
            data_inicio__gt=date.today(),
        )

        if self.instance.pk is not None:
            self.fields['promocoes'].initial = self.instance.promocoes.all()

            self.fields['promocoes'].queryset = Promocao.promocoes.filter(
                loja__scope=scope,
                data_inicio__gt=date.today(),
            ).annotate(
                desconto=ExpressionWrapper(
                    self.instance.preco_de_venda * F('porcentagem_desconto') / 100,
                    output_field=DecimalField(
                        _('Desconto'), max_digits=10, decimal_places=2
                    ),
                ),
                preco_com_desconto=ExpressionWrapper(
                    self.instance.preco_de_venda - F('desconto'),
                    output_field=DecimalField(
                        _('Desconto'), max_digits=10, decimal_places=2
                    ),
                ),
            )

    def save(self, commit: bool = True) -> Any:
        instance = super().save(commit=False)

        instance.promocoes.clear()

        for promocao in self.cleaned_data['promocoes']:
            try:
                validate_unique_promocao(instance, promocao)
                instance.promocoes.add(promocao)
            except Exception as e:
                self.add_error('promocoes', e)

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class ProdutosPorPromocaoForm(NameFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'produtos_por_promocao'

    produtos = CustomModelMultipleChoiceField(
        queryset=Produto.produtos.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label=_('Produtos'),
    )

    class Meta:
        model = Promocao
        fields = ['produtos']

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Salvar')

    def __init__(self, scope=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        self.fields['produtos'].queryset = Produto.produtos.filter(
            loja__scope=scope
        ).annotate(
            desconto=ExpressionWrapper(
                F('preco_de_venda') * (self.instance.porcentagem_desconto / 100),
                output_field=DecimalField(
                    _('Desconto'), max_digits=10, decimal_places=2
                ),
            ),
            preco_com_desconto=F('preco_de_venda') - F('desconto'),
        )

    def full_clean(self) -> None:
        super().full_clean()

        if self.instance.data_inicio < date.today():
            self.add_error(
                'data_inicio', _('A data de início não pode ser no passado.')
            )

            raise forms.ValidationError(_('A data de início não pode ser no passado.'))

    def save(self, commit: bool = True):
        instance = super().save(commit=False)

        instance.produtos.clear()

        for produto in self.cleaned_data['produtos']:
            try:
                validate_unique_promocao(produto, instance)
                instance.produtos.add(produto)
            except Exception as e:
                self.add_error('produtos', e)

        if commit:
            instance.save()
            self.save_m2m()

        return instance


class DuplicarPromocaoForm(NameFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'duplicar_promocao'

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
    promocao = forms.IntegerField(widget=forms.HiddenInput(), required=False)

    fields_loja_check = ['promocao']

    class Meta:
        model = Promocao
        fields = ['data_inicio', 'produtos']

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Duplicar')

    def __init__(self, scope=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'duplicar_promocao_form'

        instance = None
        if kwargs.get('instance'):
            instance = kwargs['instance']
            self.fields['produtos'].initial = [instance.produtos]

        if scope is not None:
            produtos_queryset = Produto.produtos.filter(loja__scope=scope)
            if instance is not None:
                produtos_queryset = produtos_queryset.annotate(
                    desconto=ExpressionWrapper(
                        F('preco_de_venda') * (instance.porcentagem_desconto / 100),
                        output_field=DecimalField(
                            _('Desconto'), max_digits=10, decimal_places=2
                        ),
                    ),
                    preco_com_desconto=F('preco_de_venda') - F('desconto'),
                )

            self.fields['produtos'].queryset = produtos_queryset
            self.scope = scope
            self.errors.clear()

    def clean_promocao(self):
        promocao = self.cleaned_data.get('promocao')

        if promocao is None:
            return None

        self.cleaned_data['promocao'] = Promocao.promocoes.get(pk=promocao)
        return self.cleaned_data['promocao']
    
    def save(self, commit: bool = ...) -> Any:
        instance = self.instance

        if instance.pk is None:
            instance = self.cleaned_data.get('promocao')

        if instance is None:
            instance = super().save(commit=False)

        replicate = instance.clonar_promocao(
            self.cleaned_data['data_inicio'], commit=False
        )

        produtos = []

        for produto in self.cleaned_data['produtos']:
            try:
                validate_unique_promocao(produto, replicate)
                produtos.append(produto)
            except Exception as e:
                self.add_error('produtos', e)

        if commit:
            replicate.save()
            replicate.produtos.set(produtos)

        return replicate


class PromocaoForm(NameFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'promocao'

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

    data_inicio = forms.DateField(
        label=_('Data de inicio'),
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=date.today(),
    )

    class Meta:
        model = Promocao
        fields = [
            'descricao',
            'data_inicio',
            'porcentagem_desconto',
            'produtos',
            'numero_de_periodos',
            'unidades_de_tempo_por_periodo',
        ]

    def get_submit_button(self) -> Submit:
        return Submit(self.submit_name(), 'Salvar')

    def __init__(self, scope=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        if scope is not None:
            self.scope = scope
            self.fields['produtos'].queryset = Produto.produtos.filter(
                loja__scope=scope
            )

        if self.instance.pk is not None:
            self.fields['produtos'].queryset.annotate(
                desconto=ExpressionWrapper(
                    F('preco_de_venda') * (self.instance.porcentagem_desconto / 100),
                    output_field=DecimalField(
                        _('Desconto'), max_digits=10, decimal_places=2
                    ),
                ),
                preco_com_desconto=F('preco_de_venda') - F('desconto'),
            )

    def clean_unidades_de_tempo_por_periodo(self):
        valor = self.cleaned_data.get('unidades_de_tempo_por_periodo')

        try:
            return int(valor)
        except ValueError:
            raise forms.ValidationError(_('Selecione uma unidade de tempo válida.'))

    def save(self, commit=True):
        periodo = Periodo.periodos.create(
            numero_de_periodos=self.cleaned_data.get('numero_de_periodos'),
            unidades_de_tempo_por_periodo=self.cleaned_data.get(
                'unidades_de_tempo_por_periodo'
            ),
        )
        promocao = super().save(commit=False)
        promocao.periodo = periodo
        promocao.loja = Loja.lojas.get(scope=self.scope)

        produtos = []

        for produto in self.cleaned_data['produtos']:
            try:
                validate_unique_promocao(produto, promocao)
                produtos.append(produto)
            except Exception as e:
                self.add_error('produtos', _(f"Produto {produto} já está em outra promoção durante o mesmo periodo."))

        if commit:
            promocao.save()
            promocao.produtos.set(produtos)

        return promocao


class FiltroPromocaoForm(CrispyFormMixin, forms.Form):
    ORDER_CHOICES = [
        ('porcentagem_desconto', _('Menor desconto')),
        ('-porcentagem_desconto', _('Maior desconto')),
        ('data_inicio', _('Menor data de início')),
        ('-data_inicio', _('Maior data de início')),
        ('id', _("Padrão")),
    ]

    ordem = forms.ChoiceField(label=_('Ordem'), choices=ORDER_CHOICES, required=False)

    STATUS_CHOICES = [
        (0, _('Todos')),
        (1, _('Ativas')),
        (2, _('Concluidas')),
        (3, _('Agendadas')),
    ]

    status = forms.ChoiceField(
        label=_('Status'), choices=STATUS_CHOICES, required=False
    )

    produtos = forms.ModelMultipleChoiceField(
        label=_('Produtos presentes'), queryset=Produto.produtos.all(), required=False
    )

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Filtrar')

    def __init__(self, data=None, scope=None, *args, **kwargs):
        super().__init__(data=data, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'get'
        self.Meta.filter_arguments = {'produtos': 'produtos__in', 'status': ''}

        if scope is not None:
            self.fields['produtos'].queryset = Produto.produtos.filter(
                loja__scope=scope
            )

    class Meta:
        order_arguments = ['ordem']
        filter_arguments = {}

    def full_clean(self):
        super().full_clean()

        if not hasattr(self, 'cleaned_data'):
            return

        status = self.cleaned_data['status']
        match status:
            case '0':
                pass
            case '1':
                self.cleaned_data['status'] = date.today() - F(
                    'periodo__numero_de_periodos'
                ) * F('periodo__unidades_de_tempo_por_periodo')
                self.Meta.filter_arguments['status'] = 'data_inicio__gte'
                self.cleaned_data['data_hoje'] = date.today()
                self.Meta.filter_arguments['data_hoje'] = 'data_inicio__lte'
            case '2':
                self.cleaned_data['status'] = date.today() - F(
                    'periodo__numero_de_periodos'
                ) * F('periodo__unidades_de_tempo_por_periodo')
                self.Meta.filter_arguments['status'] = 'data_inicio__lt'
            case '3':
                self.cleaned_data['status'] = date.today()
                self.Meta.filter_arguments['status'] = 'data_inicio__gt'

        if (
            'produtos' in self.Meta.filter_arguments
            and len(self.cleaned_data['produtos']) == 0
        ):
            self.Meta.filter_arguments.pop('produtos')
