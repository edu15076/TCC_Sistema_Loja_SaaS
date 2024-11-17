from django.db import models
from django.contrib.postgres.aggregates import ArrayAgg
from django.utils.translation import gettext_lazy as _

from scope_auth.models import AbstractUsernamePerScope, UsernamePerScopeManager, Scope


__all__ = ('PessoaUsuarioManager', 'PessoaUsuario')


class PessoaUsuarioManager(UsernamePerScopeManager):
    def pessoas_per_scope(self):
        return self.values('scope').annotate(pessoas=ArrayAgg('pessoa_ptr'))

    def filter_by_scope(self, /, scope: Scope = None):
        if scope is None:
            scope = Scope.scopes.default_scope()
        return self.filter(scope=scope)


class PessoaUsuario(AbstractUsernamePerScope):
    codigo_pessoa = models.CharField(_('Código'), max_length=14, db_column='codigo')

    codigos = PessoaUsuarioManager()

    USERNAME_FIELD = 'codigo_pessoa'

    def __repr__(self):
        return f'<PessoaUsuario: (codigo: {self.codigo_pessoa}, scope: {self.scope})>'

    def __str__(self):
        return self.__repr__()
