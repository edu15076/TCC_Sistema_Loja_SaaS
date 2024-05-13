from django.db import models

from scope_auth.models import (AbstractUserPerScopeWithEmail,
                               UserPerScopeWhitEmailManager)

from .pessoa import Pessoa, PessoaManager


class UsuarioGenericoManager(UserPerScopeWhitEmailManager):
    pass


class AbstractUsuarioGenerico(AbstractUserPerScopeWithEmail, Pessoa):
    pessoa = models.OneToOneField(Pessoa, on_delete=models.CASCADE, parent_link=True,
                                  primary_key=True, related_name='usuario')

    usuarios = UsuarioGenericoManager()

    USERNAME_PER_SCOPE_FIELD = 'codigo_escopo_pair'

    class Meta:
        abstract = True

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        return self.nome_completo

    def get_short_name(self):
        """Return the short name for the user."""
        return self.primeiro_nome

    def enviar_email_para_usuario(self, subject, message, from_email=None, **kwargs):
        """Envia um email para esse usuário."""
        self.email_user(subject, message, from_email, **kwargs)


class UsuarioGenerico(AbstractUsuarioGenerico):
    pass
