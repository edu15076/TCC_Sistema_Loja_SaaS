from decimal import Decimal

from django.contrib.auth.models import Group
from django.db import models
from django.db.models import F, Model
from django.db.models.functions import Coalesce

from common.models import (
    UsuarioGenericoPessoaFisica,
    UsuarioGenericoPessoaFisicaManager,
    UsuarioGenericoPessoaFisicaQuerySet,
    LojaScope,
)

__all__ = (
    'Funcionario',
    'GerenteDeRH',
    'GerenteFinanceiro',
    'GerenteDeEstoque',
    'Caixeiro',
    'Vendedor',
)

from loja.models.trabalhacaixa import TrabalhaCaixa
from util.decorators import CachedClassProperty

from util.models import cast_to_model


class FuncionarioQuerySet(UsuarioGenericoPessoaFisicaQuerySet):
    def complete(self):
        return (
            super()
            .complete()
            .defer('pessoa_usuario__scope__loja__logo')
            .select_related('pessoa_usuario__scope__loja')
            .annotate(loja=F('pessoa_usuario__scope__loja'))
        )

    def simple(self):
        return self.values(
            'telefone',
            'email',
            'scope',
            'nome',
            'sobrenome',
            'data_nascimento',
            'cpf',
            'loja',
        )


class FuncionarioManager(UsuarioGenericoPessoaFisicaManager):
    def get_queryset(self):
        return FuncionarioQuerySet(self.model, using=self._db).complete()

    def criar_funcionario(
        self,
        cpf: str,
        loja=None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        usuario = self.criar_usuario(
            cpf=cpf,
            scope=loja.scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )
        return usuario


class Funcionario(UsuarioGenericoPessoaFisica):
    usuario = models.OneToOneField(
        UsuarioGenericoPessoaFisica,
        models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='funcionario_loja',
    )

    _porcentagem_comissao = models.DecimalField(
        max_digits=4, decimal_places=2, null=True
    )

    funcionarios = FuncionarioManager()

    @CachedClassProperty
    def papel_group(cls):
        return None

    @CachedClassProperty
    def papel_por_funcionario(self):
        return {
            'loja_gerentes_de_rh': GerenteDeRH,
            'loja_gerentes_financeiros': GerenteFinanceiro,
            'loja_gerentes_de_estoque': GerenteDeEstoque,
            'loja_caixeiros': Caixeiro,
            'loja_vendedores': Vendedor,
        }

    @property
    def scope(self) -> LojaScope:
        return LojaScope.from_scope(super().scope)

    @scope.setter
    def scope(self, scope: LojaScope):
        self.pessoa_usuario.scope = cast_to_model(scope, LojaScope)

    @property
    def loja(self):
        if not hasattr(self.scope, 'loja'):
            raise ValueError('O funcionário da loja não é de nenhuma loja')
        return self.scope.loja

    @loja.setter
    def loja(self, loja):
        if isinstance(loja, int):
            self.scope = LojaScope.scopes.get(scope=loja)
        else:
            self.scope = loja.scope
        self.scope = loja

    def adicionar_papel(self, group: Group):
        self.groups.add(group)

    def adicionar_papeis(self, *groups: Group):
        self.groups.add(*groups)

    def remover_papel(self, group: Group):
        self.groups.remove(group)


class FuncionarioPapelQuerySet(FuncionarioQuerySet):
    def complete(self):
        return (
            super()
            .complete()
            .filter(groups=self.model.papel_group)
        )


class FuncionarioPapelManager(FuncionarioManager):
    def get_queryset(self):
        return FuncionarioQuerySet(self.model, using=self._db).complete()


class FuncionarioPapel(Funcionario):
    def save(self, *args, **kwargs):
        is_being_created = self.pk is None
        super().save(*args, **kwargs)
        if is_being_created and self.papel_group is not None:
            self.groups.add(self.papel_group)

    class Meta:
        proxy = True


class GerenteDeRH(FuncionarioPapel):
    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_de_rh')

    gerentes_de_rh = FuncionarioPapelManager()

    class Meta:
        proxy = True


class GerenteFinanceiro(FuncionarioPapel):
    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_financeiros')

    gerentes_financeiros = FuncionarioPapelManager()

    class Meta:
        proxy = True


class GerenteDeEstoque(FuncionarioPapel):
    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_de_estoque')

    gerentes_de_estoque = FuncionarioPapelManager()

    class Meta:
        proxy = True


class Caixeiro(FuncionarioPapel):
    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_caixeiros')

    caixeiros = FuncionarioPapelManager()
    
    class Meta:
        proxy = True

    def associar_caixa(self, caixa, horarios):
        for horario in horarios:
            TrabalhaCaixa.objects.create(
                caixeiro=self,
                caixa=caixa,
                trabalho_por_dia=horario
            )


class VendedorQuerySet(FuncionarioQuerySet):
    def complete(self):
        return (
            super()
            .complete()
            .annotate(
                porcentagem_comissao=Coalesce(F('_porcentagem_comissao'), Decimal(0.0))
            )
        )

    def simple(self):
        return self.values(
            'telefone',
            'email',
            'scope',
            'nome',
            'sobrenome',
            'data_nascimento',
            'cpf',
            'loja',
            'porcentagem_comissao',
        )


class VendedorManager(FuncionarioPapelManager):
    def get_queryset(self):
        return super().get_queryset().annotate(
            porcentagem_comissao=Coalesce(F('_porcentagem_comissao'), Decimal(0.0))
        )


class Vendedor(FuncionarioPapel):
    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_vendedores')

    @property
    def porcentagem_comissao(self):
        return (
            self._porcentagem_comissao
            if self._porcentagem_comissao is not None
            else 0.0
        )

    @porcentagem_comissao.setter
    def porcentagem_comissao(self, porcentagem_comissao: float):
        self._porcentagem_comissao = porcentagem_comissao

    vendedores = VendedorManager()

    class Meta:
        proxy = True
