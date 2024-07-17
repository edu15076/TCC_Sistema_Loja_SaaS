from django.contrib.auth.forms import BaseUserCreationForm

from scope_auth.models import Scope
from .pessoa_forms import PessoaCreationForm, PessoaFisicaCreationForm, \
    PessoaJuridicaCreationForm
from ..models import UsuarioGenerico, Pessoa, PessoaUsuario, \
    UsuarioGenericoPessoaFisica, UsuarioGenericoPessoaJuridica


class UsuarioGenericoCreationForm(BaseUserCreationForm, PessoaCreationForm):
    error_messages = (BaseUserCreationForm.error_messages
                      | PessoaCreationForm.error_messages)

    def __init__(self, *args, scope: Scope, **kwargs):
        super().__init__(*args, **kwargs)
        self.scope = scope

    def _save_pessoa_usuario(self, instance):
        pessoa_usuario = PessoaUsuario.codigos.get_or_create_by_natural_key(
            codigo_pessoa=instance.codigo, scope=self.scope
        )
        instance.pessoa_usuario = pessoa_usuario

    def save(self, commit=True):
        user: UsuarioGenerico = super().save(commit=False)
        self._save_pessoa_usuario(user)

        if commit:
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user

    class Meta:
        model = UsuarioGenerico
        fields = ('codigo', 'email', 'telefone')


class UsuarioGenericoPessoaFisicaCreationForm(UsuarioGenericoCreationForm,
                                              PessoaFisicaCreationForm):
    error_messages = (UsuarioGenericoCreationForm.error_messages
                      | PessoaFisicaCreationForm.error_messages)

    class Meta:
        model = UsuarioGenericoPessoaFisica
        fields = ('codigo', 'email', 'telefone', 'nome', 'sobrenome', 'data_nascimento')


class UsuarioGenericoPessoaJuridicaCreationForm(UsuarioGenericoCreationForm,
                                                PessoaJuridicaCreationForm):
    error_messages = (UsuarioGenericoCreationForm.error_messages
                      | PessoaJuridicaCreationForm.error_messages)

    class Meta:
        model = UsuarioGenericoPessoaJuridica
        fields = ('codigo', 'email', 'telefone', 'nome_fantasia', 'razao_social')
