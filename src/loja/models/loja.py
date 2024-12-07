import os
import shutil
from contextlib import suppress

from django.conf import settings
from django.db import models
from django.db.models import OuterRef, Subquery

from common.models import LojaScope
from .funcionario import Funcionario, FuncionarioQuerySet

__all__ = ('Loja',)


def loja_path(instance, filename):
    return f'lojas/loja_{instance.pk}/{filename}'


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

    def funcionarios_por_loja(self):
        return self.get_queryset().funcionarios_por_loja()


class Loja(models.Model):
    scope = models.OneToOneField(
        LojaScope, on_delete=models.CASCADE, primary_key=True, related_name='loja'
    )
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to=loja_path, null=True, blank=True)

    lojas = LojaManager()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __int__(self):
        return self.pk

    @property
    def funcionarios(self):
        return Funcionario.funcionarios.filter(loja=self)

    @funcionarios.setter
    def funcionarios(self, funcionarios):
        print(funcionarios)

    def _delete_old_logo(self, old_logo):
        logo_path = os.path.join(settings.MEDIA_ROOT, old_logo.name)
        if os.path.exists(logo_path) and os.path.isfile(logo_path):
            with suppress(Exception):
                os.remove(logo_path)

    def save(self, *args, **kwargs):
        if self.pk is None and (not hasattr(self, 'scope') or self.scope is None):
            self.scope = LojaScope.scopes.create()
        if self.pk is not None:
            with suppress(Loja.DoesNotExist):
                if (old_logo := Loja.lojas.get(pk=self.pk).logo) != self.logo:
                    self._delete_old_logo(old_logo)

        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        loja_directory = os.path.join(settings.MEDIA_ROOT, f'lojas/loja_{self.pk}')

        if os.path.isdir(loja_directory):
            with suppress(Exception):
                shutil.rmtree(loja_directory)

        return self.scope.delete()
