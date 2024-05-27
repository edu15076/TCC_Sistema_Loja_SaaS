from django.db import models

from common.models import (UsuarioGenericoPessoaJuridica,
                           UsuarioGenericoPessoaJuridicaManager)
from common.models import ContratosScope
from loja.models import Loja
from util.models.singleton import AbstractSingleton


__all__ = (
    'UsuarioContratacao',
    'GerenteDeContratos',
    'ClienteContratante'
)


class UsuarioContratacaoManager(UsuarioGenericoPessoaJuridicaManager):
    def criar_usuario_contratacao(
            self, cnpj: str, password: str = None, email: str = None,
            telefone: str = None, **dados_pessoa
    ):
        return self.criar_usuario(
            cnpj=cnpj, scope=ContratosScope.instance, password=password, email=email,
            telefone=telefone, **dados_pessoa
        )


class UsuarioContratacao(UsuarioGenericoPessoaJuridica):
    usuarios = UsuarioContratacaoManager()

    class Meta:
        proxy = True


class GerenteDeContratosManager(UsuarioContratacaoManager):
    pass


class GerenteDeContratos(UsuarioContratacao, AbstractSingleton):
    gerentes = GerenteDeContratosManager()


class ClienteContratanteManager(UsuarioContratacaoManager):
    pass


class ClienteContratante(UsuarioContratacao):
    loja = models.OneToOneField(Loja, on_delete=models.CASCADE,
                                related_name='contratante')

    contratantes = ClienteContratanteManager()
