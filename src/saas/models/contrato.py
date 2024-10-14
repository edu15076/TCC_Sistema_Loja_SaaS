from django.db import models
from django.utils.translation import gettext_lazy as _


__all__ = [
    'ContratoQuerySet',
    'ContratoManager',
    'Contrato'
]


class ContratoQuerySet(models.QuerySet):
    def simple(self):
        return self.values('descricao')


class ContratoManager(models.Manager):
    def get_queryset(self):
        return ContratoQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()


class Contrato(models.Model):
    descricao = models.CharField(_('Descrição'), max_length=100, blank=True)

    pessoas = ContratoManager()