from decimal import Decimal

from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Submit, Layout
from django import forms
from django.utils.translation import gettext_lazy as _

from loja.forms.mixins import LojaValidatorFormMixin
from loja.forms.validators import ActiveFuncionarioValidator
from loja.models import Vendedor
from util.forms import CrispyFormMixin, ModelIntegerField

__all__ = (
    'AlterarComissaoVendedorForm',
)


class AlterarComissaoVendedorForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    error_messages = {
        'comissao_fora_da_porcentagem': 
            _('A comissão não pode ser menor que 0% ou maior que 100%'),
    }
    
    fields_loja_check = ['vendedor']

    vendedor = ModelIntegerField(
        required=True,
        widget=forms.HiddenInput,
        model_cls=Vendedor,
        validators=[ActiveFuncionarioValidator()]
    )
    comissao = forms.DecimalField(
        min_value=Decimal('0'), max_value=Decimal('100'), step_size=Decimal('0.01'),
        max_digits=5, decimal_places=2,
        required=True,
        label=_('Comissão'),
        widget=forms.NumberInput(
            attrs={
                'class': 'porcentagem-comissao-input check-on-blur',
                'style': 'max-width: 7rem;'
            }
        )
    )

    def get_submit_button(self) -> Submit:
        return Submit('submit', _('Submit'), css_class='d-none')

    def __init__(self, *args, disabled=False, add_is_valid=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.layout = Layout(
            'vendedor',
            AppendedText(
                'comissao', '%', template='form_fields/crispy_append_text.html'),
        )
        if disabled:
            self.fields['comissao'].widget.attrs['disabled'] = True
        if add_is_valid:
            self.add_is_valid()

    def add_is_valid(self):
        self.fields['comissao'].widget.attrs['class'] += ' is-valid'

    def clean_comissao(self):
        comissao: bool = self.cleaned_data['comissao']
        if not 0.0 <= comissao <= 100.0:
            raise forms.ValidationError(
                message=self.error_messages['comissao_fora_da_porcentagem'],
                code='comissao_fora_da_porcentagem'
            )
        return comissao

    def save(self):
        vendedor: Vendedor = self.cleaned_data['vendedor']
        comissao: bool = self.cleaned_data['comissao']
        vendedor.porcentagem_comissao = comissao
        vendedor.save()
        