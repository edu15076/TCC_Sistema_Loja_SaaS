from django.db import models

from common.models import UsuarioGenerico, UsuarioGenericoManager
from loja.models import Loja


class ContratanteManager(UsuarioGenericoManager):
    def get_queryset(self):
        return super().get_queryset().filter(groups__name='Contratante')


class GerenteManager(UsuarioGenericoManager):
    def get_queryset(self):
        return super().get_queryset().filter(groups__name='Gerentes')


class UsuarioContratacao(UsuarioGenerico):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE,
                                related_name='contratante', null=True)

    usuarios = UsuarioGenericoManager()
    contratantes = ContratanteManager()
    gerentes = GerenteManager()
