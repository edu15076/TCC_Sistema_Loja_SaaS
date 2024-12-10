from typing import Any

from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from .crispy_forms import CrispyFormMixin
from django.db.models import Q


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

        if not query:
            return {}

        return {
            f'{field}__icontains': query
            for field in self.Meta.fields
        }
    
    def is_valid(self) -> bool:
        return super().is_valid() and len(self.cleaned_data['query']) > 0
    
    def get_query_expression(self):
        query = self.cleaned_data['query']

        if not query or len(query) == 0:
            return None
        
        query_filter = Q()
        for field in self.Meta.fields:
            query_filter |= Q(**{f'{field}__icontains': query})

        return query_filter
