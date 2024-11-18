from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import OuterRef, Subquery

from common.models import LojaScope

from .funcionario import Funcionario, FuncionarioQuerySet


__all__ = ('Loja',)


class LojaQuerySet(models.QuerySet):
    def funcionarios_por_loja(self, funcionarios: FuncionarioQuerySet = None):
        if funcionarios is None:
            funcionarios = Funcionario.funcionarios.filter(
                loja=OuterRef('pk')
            ).values_list('pk', flat=True)
        return self.values('pk').annotate(funcionarios=Subquery(funcionarios))


class LojaManager(models.Manager):
    def get_queryset(self):
        return LojaQuerySet(self.model, using=self._db).defer('logo')

    def create(self, **kwargs):
        loja_scope = LojaScope.scopes.create()
        return super().create(scope=loja_scope, **kwargs)

    def funcionarios_por_loja(self):
        return self.get_queryset().funcionarios_por_loja()


class Loja(models.Model):
    scope = models.OneToOneField(
        LojaScope, on_delete=models.CASCADE, primary_key=True, related_name='loja'
    )
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='dynamic_files/images/logos_loja/')

    lojas = LojaManager()

    def __int__(self):
        return self.pk

    @property
    def funcionarios(self):
        return Funcionario.funcionarios.filter(loja=self)

    @funcionarios.setter
    def funcionarios(self, funcionarios):
        print(funcionarios)
