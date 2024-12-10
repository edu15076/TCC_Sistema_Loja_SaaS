from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from common.models import Periodo
from util.forms import QueryFormMixin, CrispyFormMixin
from util.mixins import NameFormMixin
from loja.models import Produto, Promocao


class ProdutoQueryForm(NameFormMixin, QueryFormMixin, forms.Form):
    _name = "produto_query"

    query = forms.CharField(
        label=_('Pesquisar'),
        required=False,
        max_length=128,
        widget=forms.TextInput(attrs={'placeholder': _('Digite sua pesquisa...')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'

    class Meta:
        fields = ['descricao', 'codigo_de_barras']
