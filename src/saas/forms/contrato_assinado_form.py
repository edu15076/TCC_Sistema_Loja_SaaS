from django import forms
from saas.models import ContratoAssinado


class ContratoAssinadoForm(forms.ModelForm):
    class Meta:
        model = ContratoAssinado
        fields = ['contrato', 'cliente_contratante']
        widgets = {
            'contrato': forms.Select(),
            'cliente_contratante': forms.Select(),
        }

    def save(self, commit=True):
        self.instance.vigente = True
        return super(ContratoAssinadoForm, self).save(commit=commit)
