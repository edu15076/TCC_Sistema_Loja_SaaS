from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from django import forms
from django.utils.translation import gettext_lazy as _

from ..models import Contrato
from common.models import Periodo


class ContratoForm(forms.ModelForm):
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
            'unidades_de_tempo_por_periodo',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', _('Salvar')))

    def save(self, commit: bool = True) -> Any:
        periodo = Periodo.periodos.create(
            numero_de_periodos=self.cleaned_data.get('numero_de_periodos'),
            unidades_de_tempo_por_periodo=self.cleaned_data.get(
                'unidades_de_tempo_por_periodo'
            ),
        )

        contrato = super().save(commit=False)
        contrato.periodo = periodo

        if commit:
            contrato.save()

        return contrato
