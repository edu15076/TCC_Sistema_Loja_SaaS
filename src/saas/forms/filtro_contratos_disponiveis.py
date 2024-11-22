from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from util.forms import CrispyFormMixin


class FiltroContratosDisponiveisForm(CrispyFormMixin, forms.Form):
    ORDER_CHOICES = [
        ('id', _("Padrão")),
        ('valor_por_periodo', _('Menor valor por periodo')),
        ('-valor_por_periodo', _('Maior valor por periodo')),
        ('-telas_simultaneas', _('Maior número de telas')),
        ('telas_simultaneas', _('Menor número de telas')),
    ]

    ordem = forms.ChoiceField(label=_('Ordem'), choices=ORDER_CHOICES, required=False)

    def get_submit_button(self) -> Submit:
        return Submit('submit', 'Filtrar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.helper.form_method = 'get'

    class Meta:
        order_arguments = ['ordem']
