from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from loja.models import ConfiguracaoDeVendas
from util.mixins import NameFormMixin
from util.forms import (
    CrispyFormMixin,
    CustomModelMultipleChoiceField
)


class ConfiguracaoDeVendasForm(NameFormMixin, CrispyFormMixin, forms.ModelForm):
    _name = 'configuracao_de_venda'

    def get_submit_button(self):
        return Submit(self.submit_name(), _('Salvar'))

    class Meta:
        model = ConfiguracaoDeVendas
        fields = ['limite_porcentagem_desconto_maximo']

    def __init__(self, loja=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

        # self.instance = ConfiguracaoDeVendas.objects.get(loja=loja)
        self.instance = ConfiguracaoDeVendas.configuracoes.get(loja__scope=2)

        self.fields['limite_porcentagem_desconto_maximo'].initial = self.instance.limite_porcentagem_desconto_maximo




