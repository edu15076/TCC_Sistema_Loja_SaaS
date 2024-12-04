from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from common.models import Periodo
from util.forms import QueryFormMixin, CrispyFormMixin
from loja.models import Produto, Promocao


class ProdutoQueryForm(QueryFormMixin, forms.Form):
    query = forms.CharField(
        required=True,
        max_length=128,
        widget=forms.TextInput(attrs={'placeholder': _('Digite sua pesquisa...')}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'post'
        self.helper.attrs = {'oninput': 'this.form.submit()'}

    class Meta:
        fields = ['descricao']
