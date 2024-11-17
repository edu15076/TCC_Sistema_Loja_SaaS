from common.forms import UsuarioGenericoPessoaJuridicaCreationForm
from saas.models import ClienteContratante


class ClienteContratanteCreationForm(UsuarioGenericoPessoaJuridicaCreationForm):
    error_messages = UsuarioGenericoPessoaJuridicaCreationForm.error_messages

    class Meta:
        model = ClienteContratante
        fields = UsuarioGenericoPessoaJuridicaCreationForm.Meta.fields
        labels = getattr(UsuarioGenericoPessoaJuridicaCreationForm.Meta, 'labels', {})
