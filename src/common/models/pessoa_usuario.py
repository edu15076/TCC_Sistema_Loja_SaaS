import unicodedata
from django.db import models

from scope_auth.models import AbstractUsernamePerScope, UsernamePerScopeManager, Scope

from .pessoa import Pessoa


class PessoaUsuarioManager(UsernamePerScopeManager):
    def filter_by_scope(self, /, scope: Scope = None):
        if scope is None:
            scope = Scope.scopes.default_scope()
        return self.filter(scope=scope)


class PessoaUsuario(AbstractUsernamePerScope):
    pessoa = models.ForeignKey(Pessoa, on_delete=models.CASCADE,
                               related_name='scopes')

    codigos = PessoaUsuarioManager()

    USERNAME_FIELD = 'pessoa'

    @classmethod
    def normalize_username(cls, username: str | Pessoa) -> Pessoa:
        return (
            Pessoa.pessoas.get_or_create(
                codigo=unicodedata.normalize('NFKC', username)
            )[0]
            if isinstance(username, str)
            else username
        )

    def __repr__(self):
        return f'<PessoaUsuario: (codigo: {self.pessoa}, scope: {self.scope})>'

    def __str__(self):
        return self.__repr__()
