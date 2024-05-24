from django.contrib.auth.models import Group
from django.db import models
from django.db.models import F

from common.models import (UsuarioGenericoPessoaFisica,
                           UsuarioGenericoPessoaFisicaManager,
                           UsuarioGenericoPessoaFisicaQuerySet, LojaScope,
                           UsuarioGenerico)


__all__ = (
    'Funcionario',
    'Chefe',
    'GerenteDeRH',
    'GerenteDeVendas',
    'GerenteDeEstoque',
    'Caixeiro',
    'Vendedor'
)

from util.decorators import CachedClassProperty

from util.models import cast_to_model


class FuncionarioQuerySet(UsuarioGenericoPessoaFisicaQuerySet):
    def complete(self):
        return (super().complete().defer('pessoa_usuario__scope__loja__logo')
                .select_related('pessoa_usuario__scope__loja')
                .annotate(loja=F('pessoa_usuario__scope__loja')))

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'nome', 'sobrenome', 'data_nascimento', 'cpf',
            'loja'
        )


class FuncionarioManager(UsuarioGenericoPessoaFisicaManager):
    def get_queryset(self):
        return FuncionarioQuerySet(self.model, using=self._db).complete()

    def criar_funcionario(
            self, cpf: str, loja=None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        usuario = self.criar_usuario(
            cpf=cpf, scope=loja.scope, password=password, email=email,
            telefone=telefone, **dados_pessoa
        )
        if self.model.papel_group is not None:
            usuario.groups.add(self.model.papel_group)
            usuario.save()
        return usuario

    def _criar_ou_recuperar_de_funcionario(self, funcionario: 'Funcionario',
                                           **extra_fields):
        """Cria ou recupera uma instância subclasse a partir de um funcionario"""
        funcionario.groups.add(self.model.papel_group)
        funcionario.save()
        return funcionario


class Funcionario(UsuarioGenericoPessoaFisica):
    # TODO: Adicionar fields de Funcionario

    usuario = models.OneToOneField(
        UsuarioGenerico,
        models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='funcionario_loja'
    )

    funcionarios = FuncionarioManager()

    @CachedClassProperty
    def papel_group(cls):
        return None

    @CachedClassProperty
    def papel_por_funcionario(self):
        return {
            'loja_chefes': Chefe,
            'loja_gerentes_de_rh': GerenteDeRH,
            'loja_gerentes_de_vendas': GerenteDeVendas,
            'loja_gerentes_de_estoque': GerenteDeEstoque,
            'loja_caixeiros': Caixeiro,
            'loja_vendedores': Vendedor
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

    def adicionar_papel(self, group: Group, **extra_fields):
        class_for_papel = self.papel_por_funcionario[group.name]
        class_for_papel._default_manager._criar_ou_recuperar_de_funcionario(
            self, **extra_fields)

    # TODO: Criar métodos para verificar se um usuário é de um tipo

    class Meta:
        # TODO: Definir permissões genéricas para trabalhar com o funcionário
        pass


# TODO: Avaliar possibilidade de colocar algumas das classes como proxy, como o Chefe
#       outras classes podem ter relações adicionais à funcionário


class Chefe(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='chefe'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_chefes')

    class Meta:
        permissions = (
            ('criar_chefe', 'Pode criar chefe'),
        )


class GerenteDeRH(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='gerente_de_rh'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_de_rh')


class GerenteDeVendas(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='gerente_de_vendas'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_de_vendas')


class GerenteDeEstoque(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='gerente_de_estoque'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_gerentes_de_estoque')


class Caixeiro(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='caixeiro'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_caixeiros')


class Vendedor(Funcionario):
    funcionario = models.OneToOneField(
        Funcionario,
        models.CASCADE,
        primary_key=True,
        parent_link=True,
        related_name='vendedor'
    )

    @CachedClassProperty
    def papel_group(cls):
        return Group.objects.get(name='loja_vendedores')
