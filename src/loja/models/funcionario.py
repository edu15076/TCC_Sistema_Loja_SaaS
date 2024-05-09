from django.db import models

from common.models import Pessoa, PessoaManager


class FuncionarioManager(PessoaManager):
    def get_queryset(self):
        return super().get_queryset().annotate(loja_id='codigo')


class Funcionario(Pessoa):
    funcionarios = FuncionarioManager()

    @property
    def loja(self):
        from .loja import Loja
        return Loja.lojas.get(id=self.codigo)
