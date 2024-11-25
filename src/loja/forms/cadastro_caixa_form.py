from django import forms
from loja.models.caixa import Caixa

class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['numero_identificacao', 'loja', 'ativo']
        widgets = {
            'horario_aberto': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }