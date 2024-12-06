from django.contrib.auth.models import Group
from django.db import models

from common.models import ContratosScope
from common.models import (
    UsuarioGenericoPessoaJuridica,
    UsuarioGenericoPessoaJuridicaManager,
)
from loja.models import Loja
from util.decorators import CachedClassProperty
from util.models.singleton import SingletonManager, SingletonMixin

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
        return usuario


class UsuarioContratacao(UsuarioGenericoPessoaJuridica):
    usuarios = UsuarioContratacaoManager()

    @CachedClassProperty
    def papel_group(cls) -> Group | None:
        return None

    def save(self, *args, **kwargs) -> None:
        is_being_created = self.pk is None
        super().save(*args, **kwargs)
        if is_being_created and self.papel_group is not None:
            self.groups.add(self.papel_group)

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
        Loja, on_delete=models.RESTRICT, related_name='contratante'
    )

    contratantes = ClienteContratanteManager()

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='saas_clientes_contratantes')

    def is_signing_contract(self) -> bool:
        return self.contratoassinado_set.filter(vigente=True).exists()

    def save(self, *args, **kwargs):
        self.loja = (
            Loja.lojas.create(nome=self.nome_fantasia)
            if not hasattr(self, 'loja') or self.loja is None
            else self.loja
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        loja = self.loja
        delete_result = super().delete(*args, **kwargs)
        loja_delete_result = loja.delete()
        return (
            delete_result[0] + loja_delete_result[0],
            delete_result[1] | loja_delete_result[1],
        )

    def delete_dados_loja(self, *args, **kwargs):
        old_loja: Loja = self.loja
        self.loja = Loja.lojas.create()
        self.save()
        return old_loja.delete(*args, **kwargs)
