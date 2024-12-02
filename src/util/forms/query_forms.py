from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .crispy_forms import CrispyFormMixin


class QueryFormMixin(CrispyFormMixin):
    query = forms.CharField(
        required=False,
        max_length=128,
        widget=forms.TextInput(attrs={'placeholder': _('Digite sua pesquisa...')}),
    )

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Pesquisar')

    def _get_queryset(self) -> Any:
        return (
            self.queryset if self.queryset else self.model._meta.default_manager.all()
        )

    def get_parameters(self) -> dict[str, Any]:
        query = self.cleaned_data['query']

        if query is None:
            return {}

        return {f'{field}__icontains': query for field in self.Meta.fields}
