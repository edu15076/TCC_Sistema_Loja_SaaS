from django.db import transaction

from common.forms import UsuarioGenericoPessoaJuridicaCreationForm
from saas.models import ClienteContratante
from loja.models import Loja

class ClienteContratanteCreationForm(UsuarioGenericoPessoaJuridicaCreationForm):
    error_messages = UsuarioGenericoPessoaJuridicaCreationForm.error_messages

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            self._save_pessoa_usuario(user)
            user.loja = (Loja.lojas.create()
                         if not hasattr(self, 'loja') or self.loja is None
                         else user.loja)
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
            if user.papel_group is not None:
                user.groups.set([user.papel_group])

        return user

    class Meta:
        model = ClienteContratante
        fields = UsuarioGenericoPessoaJuridicaCreationForm.Meta.fields
        labels = getattr(UsuarioGenericoPessoaJuridicaCreationForm.Meta, 'labels', {})
