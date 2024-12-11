from crispy_forms.bootstrap import AppendedText
from crispy_forms.layout import Submit, Layout
from django import forms
from django.utils.translation import gettext_lazy as _

from loja.models import ConfiguracaoDeVendas
from util.mixins import NameFormMixin
from .mixins import LojaValidatorFormMixin
from util.forms import CrispyFormMixin


class ConfiguracaoDeVendasForm(
    NameFormMixin, LojaValidatorFormMixin, CrispyFormMixin, forms.ModelForm
):
    _name = 'configuracao_de_venda'
    should_check_model_form = True

    def get_submit_button(self):
        return Submit(self.submit_name(), _('Salvar'))

    class Meta:
        model = ConfiguracaoDeVendas
        fields = ['limite_porcentagem_desconto_maximo']

    def __init__(self, loja=None, *args, **kwargs):
        super().__init__(loja=loja, *args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            AppendedText(
                'limite_porcentagem_desconto_maximo', '%', template='form_fields/crispy_append_text.html'),
        )

        self.instance = ConfiguracaoDeVendas.configuracoes.get(loja=loja)

        self.fields['limite_porcentagem_desconto_maximo'].initial = (
            self.instance.limite_porcentagem_desconto_maximo
        )
