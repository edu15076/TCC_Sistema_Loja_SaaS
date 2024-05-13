from django.db import models

from common.models.escopo import EscopoLoja


class LojaManager(models.Manager):
    pass


class Loja(EscopoLoja):
    nome = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='dynamic_files/images/logos_loja/')

    lojas = LojaManager()

    @property
    def funcionarios(self):
        from .funcionario import Funcionario
        return Funcionario.funcionarios.filter(loja_id=self.id)

    @property
    def usuarios(self):
        return self.funcionarios.select_related('usuario')
