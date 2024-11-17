from django.contrib.auth.models import Group
from django.db import models, transaction

from common.models import (
    UsuarioGenericoPessoaJuridica,
    UsuarioGenericoPessoaJuridicaManager,
)
from common.models import ContratosScope
from loja.models import Loja
from util.decorators import CachedClassProperty
from util.models.singleton import AbstractSingleton, SingletonManager, SingletonMixin

__all__ = ('UsuarioContratacao', 'GerenteDeContratos', 'ClienteContratante')


class UsuarioContratacaoManager(UsuarioGenericoPessoaJuridicaManager):
    def criar_usuario_contratacao(
        self,
        cnpj: str,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        usuario = self.criar_usuario(
            cnpj=cnpj,
            scope=ContratosScope.instance,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )
        if self.model.papel_group is not None:
            usuario.groups.set([self.model.papel_group])
        return usuario


class UsuarioContratacao(UsuarioGenericoPessoaJuridica):
    usuarios = UsuarioContratacaoManager()

    @CachedClassProperty
    def papel_group(cls) -> Group | None:
        return None

    class Meta:
        proxy = True


class GerenteDeContratosManager(UsuarioContratacaoManager, SingletonManager):
    pass


class GerenteDeContratos(UsuarioContratacao, SingletonMixin):
    gerente = GerenteDeContratosManager()

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='saas_gerente_de_contratos')


class ClienteContratanteManager(UsuarioContratacaoManager):
    def _get_cleaned_user(self, kwargs):
        username, password, extra_fields = super()._get_cleaned_user(kwargs)
        extra_fields['loja'] = Loja.lojas.create()
        return username, password, extra_fields


class ClienteContratante(UsuarioContratacao):
    loja = models.OneToOneField(
        Loja, on_delete=models.CASCADE, related_name='contratante'
    )

    contratantes = ClienteContratanteManager()

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='saas_clientes_contratantes')

    @transaction.atomic
    def save(self, *args, **kwargs):
        if self._state.adding:
            self.loja = (Loja.lojas.create()
                         if not hasattr(self, 'loja') or self.loja is None
                         else self.loja)
        return super().save(*args, **kwargs)
