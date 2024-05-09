from django.db import models
from django.utils.translation import gettext_lazy as _

from .escopo import Escopo


class CodigoEscopoPairManager(models.Manager):
    def get_codigos(self, *, escopo: Escopo = None):
        if escopo is None:
            return self.values('codigo')
        return self.values('codigo').filter(escopo=escopo)


class CodigoEscopoPair(models.Model):
    codigo = models.CharField(_('CPF ou CNPJ'), max_length=14)
    escopo = models.ForeignKey(Escopo, on_delete=models.CASCADE)

    objects = CodigoEscopoPairManager()

    def __str__(self):
        return f'(codigo: {self.codigo}, escopo: {self.escopo})'

    def __repr__(self):
        return str(self)

    class Meta:
        unique_together = (('codigo', 'escopo'),)
