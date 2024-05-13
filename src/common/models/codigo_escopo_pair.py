from django.db import models
from django.utils.translation import gettext_lazy as _

from scope_auth.models import UsernamePerScopeManager, AbstractUsernamePerScope
from scope_auth.models import Scope


class CodigoScopePairManager(UsernamePerScopeManager):
    def get_codigos(self, *, escopo: Scope = None):
        if escopo is None:
            return self.values('codigo')
        return self.values('codigo').filter(escopo=escopo)


class CodigoScopePair(AbstractUsernamePerScope):
    codigo = models.CharField(_('CPF ou CNPJ'), max_length=14)

    objects = CodigoScopePairManager()

    USERNAME_FIELD = 'codigo'

    def __str__(self):
        return f'{{codigo: {self.codigo}, scope: {self.scope}}}'

    def __repr__(self):
        return str(self)
