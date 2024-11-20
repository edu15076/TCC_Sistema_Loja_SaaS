from django.db import transaction

from common.forms import UsuarioGenericoPessoaJuridicaCreationForm
from saas.models import ClienteContratante
from loja.models import Loja

class ClienteContratanteCreationForm(UsuarioGenericoPessoaJuridicaCreationForm):
    error_messages = UsuarioGenericoPessoaJuridicaCreationForm.error_messages

    class Meta:
        model = ClienteContratante
        fields = UsuarioGenericoPessoaJuridicaCreationForm.Meta.fields
        labels = getattr(UsuarioGenericoPessoaJuridicaCreationForm.Meta, 'labels', {})
