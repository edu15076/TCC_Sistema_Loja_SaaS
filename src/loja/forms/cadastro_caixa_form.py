from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from loja.models.caixa import Caixa


class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['numero_identificacao', 'loja', 'ativo']
        widgets = {
            'numero_identificacao': forms.TextInput(
                attrs={'placeholder': 'Número de Identificação'}),
        }

    def __init__(self, *args, action: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.action = action

        if self.action:
            self.fields['loja'].widget.attrs['class'] = 'special-class'

    def clean_numero_identificacao(self):
        numero = self.cleaned_data.get('numero_identificacao')
        if not numero.isalnum():
            raise forms.ValidationError(
                "O número de identificação deve ser alfanumérico.")
        return numero

    def create_helper(self, add_submit_button=True):
        # TODO: Usar CrispyFormMixin
        helper = FormHelper()
        helper.form_method = 'post'
        if add_submit_button:
            helper.add_input(Submit('submit', 'Submit'))
        return helper
