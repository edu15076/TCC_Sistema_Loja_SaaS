from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Contrato
from common.models import Periodo
from util.forms import CrispyFormMixin

class ContratoForm(CrispyFormMixin, forms.ModelForm):
    numero_de_periodos = forms.IntegerField(
        label=_('Número de períodos'),
        min_value=0,
        error_messages={'min_value': _('Número não pode ser negativo.')}
    )
    
    unidades_de_tempo_por_periodo = forms.ChoiceField(
        label=_('Unidade de tempo por período'),
        choices=Periodo.UnidadeDeTempo.choices,
        initial=Periodo.UnidadeDeTempo.MES
    )

    class Meta:
        model = Contrato
        fields = [
            'descricao', 
            'ativo', 
            'valor_por_periodo', 
            'telas_simultaneas', 
            'taxa_de_multa', 
            'tempo_maximo_de_atraso_em_dias', 
            'numero_de_periodos', 
            'unidades_de_tempo_por_periodo'
        ]

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Salvar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

    def save(self, commit: bool = True) -> Any:
        periodo = Periodo.periodos.create(
            numero_de_periodos=self.cleaned_data.get('numero_de_periodos'),
            unidades_de_tempo_por_periodo=self.cleaned_data.get('unidades_de_tempo_por_periodo')
        )

        contrato = super().save(commit=False)
        contrato.periodo = periodo

        if commit:
            contrato.save()
            
        return contrato
    
class FiltroContratoForm(CrispyFormMixin, forms.Form):
    STATUS_CHOICES = [
        ('todos', _('Todos')),
        (True, _('Ativos')),
        (False, _('Inativos')),
    ]
    ORDER_CHOICES = [
        ('valor_por_periodo', _('Menor valor por periodo')),
        # TODO ('telas_simultaneas',)
        ('-valor_por_periodo', _('Maior valor por periodo')),
        ('valor_total', _('Menor valor total')),
        ('-valor_total', _('Maior valor total')),
        ('id', _("Padrão")),
    ]

    ativo = forms.ChoiceField(
        label=_('Status dos Contratos'),
        choices=STATUS_CHOICES,
        initial=None,
        required=False
    )

    ordem = forms.ChoiceField(
        label=_('Ordem'),
        choices=ORDER_CHOICES,
        required=False
    )
    
    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Filtrar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'get'

    class Meta:
        order_arguments = ['ordem']
        filter_arguments = ['ativo']

    

        
