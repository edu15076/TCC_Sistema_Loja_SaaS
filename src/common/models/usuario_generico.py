from contextlib import suppress

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from scope_auth.models import (
    Scope,
    AbstractUserPerScopeWithEmail,
    UserPerScopeWhitEmailManager,
)
from util.decorators import CachedClassProperty
from util.models import cast_to_model
from .pessoa import PessoaFisica, PessoaJuridica, Pessoa
from .pessoa_usuario import PessoaUsuario

__all__ = (
    'UsuarioGenericoQuerySet',
    'UsuarioGenericoManager',
    'AbstractUsuarioGenerico',
    'UsuarioGenerico',
    'UsuarioGenericoSimpleQuerySet',
    'UsuarioGenericoSimpleManager',
    'UsuarioGenericoSimple',
    'UsuarioGenericoPessoaQuerySet',
    'UsuarioGenericoPessoaManager',
    'UsuarioGenericoPessoa',
    'UsuarioGenericoPessoaFisicaQuerySet',
    'UsuarioGenericoPessoaFisicaManager',
    'UsuarioGenericoPessoaFisica',
    'UsuarioGenericoPessoaJuridicaQuerySet',
    'UsuarioGenericoPessoaJuridicaManager',
    'UsuarioGenericoPessoaJuridica',
)


class UsuarioGenericoQuerySet(models.QuerySet):
    def usuarios_per_scope(self):
        return self.values(scope='pessoa_usuario__scope').annotate(
            pessoas=ArrayAgg('pessoa_usuario__codigo')
        )

    def complete(self):
        return self.select_related('pessoa_usuario')


class UsuarioGenericoManager(UserPerScopeWhitEmailManager):
    def get_queryset(self):
        return UsuarioGenericoQuerySet(self.model, using=self._db).complete()

    def get_by_codigo(self, codigo: str, escopo: Scope = None):
        return super().get_by_natural_key(
            username=PessoaUsuario.codigos.get(codigo_pessoa=codigo), scope=escopo
        )


class AbstractUsuarioGenerico(AbstractUserPerScopeWithEmail, Pessoa):
    pessoa_usuario = models.OneToOneField(
        PessoaUsuario,
        on_delete=models.CASCADE,
        verbose_name=_('Código'),
        related_name='usuario',
        editable=False,
        unique=True,
        primary_key=True,
    )

    usuarios = UsuarioGenericoManager()

    USERNAME_PER_SCOPE_FIELD = 'pessoa_usuario'

    class Meta:
        abstract = True

    def enviar_email_para_usuario(self, subject, message, from_email=None, **kwargs):
        """Envia um email para esse usuário."""
        self.email_user(subject, message, from_email, **kwargs)

    def __repr__(self):
        return (
            f'<{self.__class__.__name__}: {{codigo={self.codigo}, '
            f'scope={self.pessoa_usuario.scope}}}>'
        )

    def __str__(self):
        return repr(self)

    def clean(self):
        AbstractUserPerScopeWithEmail.clean(self)
        Pessoa.clean(self)

    def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
        AbstractUserPerScopeWithEmail.full_clean(
            self, exclude, validate_unique, validate_constraints
        )
        Pessoa.full_clean(self, exclude, validate_unique, validate_constraints)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class UsuarioGenerico(AbstractUsuarioGenerico):
    pass


class UsuarioGenericoSimpleQuerySet(UsuarioGenericoQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {'scope': F('pessoa_usuario__scope')}

    @CachedClassProperty
    def _aliased_fields(cls):
        return UsuarioGenericoSimpleQuerySet._annotated_fields

    def _complete(self):
        return self.alias(**self._aliased_fields)

    def complete(self):
        return super().complete()._complete().annotate(**self._annotated_fields)

    def simple(self):
        return self.values('telefone', 'email', 'pessoa_ptr', 'scope')


class UsuarioGenericoSimpleManager(UsuarioGenericoManager):
    def get_queryset(self):
        return UsuarioGenericoSimpleQuerySet(self.model, using=self._db).complete()

    def from_usuarios_queryset(self, qs):
        return self.filter(pk__in=qs)

    def simple(self):
        return self.get_queryset().simple()


class UsuarioGenericoSimple(UsuarioGenerico):
    usuarios = UsuarioGenericoSimpleManager()

    @classmethod
    def from_usuario(cls, usuario):
        usuario.__class__ = UsuarioGenericoSimple
        return usuario

    @classmethod
    def cast_para_primeira_subclasse(
        cls,
        subclasses: list[type['UsuarioGenericoSimple']],
        usuario: 'UsuarioGenericoSimple',
    ):
        for usuario_class in subclasses:
            with suppress(usuario_class.DoesNotExist):
                return usuario_class._default_manager.get(pk=usuario.pk)
        return usuario

    @property
    def scope(self) -> Scope:
        return self.pessoa_usuario.scope

    @scope.setter
    def scope(self, scope: Scope):
        self.pessoa_usuario.scope = cast_to_model(scope, Scope)

    def save(self, *args, **kwargs):
        if hasattr(self, 'pessoa_usuario'):
            self.pessoa_usuario.save()
        super().save(*args, **kwargs)

    class Meta:
        proxy = True


class UsuarioGenericoPessoaQuerySet(UsuarioGenericoSimpleQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {'scope': F('pessoa_usuario__scope')}

    @CachedClassProperty
    def _aliased_fields(cls):
        return super()._aliased_fields | UsuarioGenericoPessoaQuerySet._annotated_fields

    def simple(self):
        return self.values('telefone', 'email', 'scope', 'codigo')


class UsuarioGenericoPessoaManager(UsuarioGenericoSimpleManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaQuerySet(self.model, using=self._db).complete()

    def criar_usuario(
        self,
        codigo: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return self.create_user_by_natural_key(
            codigo=codigo,
            codigo_pessoa=codigo,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )

    def criar_superusuario(
        self,
        codigo: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return self.create_superuser_by_natural_key(
            codigo=codigo,
            codigo_pessoa=codigo,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )

    class _Builder(UsuarioGenericoSimpleManager._Builder):
        def build_user_by_natural_key(self):
            return self._manager.criar_usuario(**self._kwargs)

        def build_superuser_by_natural_key(self):
            return self._manager.criar_superusuario(**self._kwargs)

        def build_usuario(self):
            return self.build_user_by_natural_key()

        def build_superusuario(self):
            return self.build_superuser_by_natural_key()


class UsuarioGenericoPessoa(UsuarioGenericoSimple):
    usuarios = UsuarioGenericoPessoaManager()

    @classmethod
    def from_usuario(cls, usuario: AbstractUsuarioGenerico) -> 'UsuarioGenericoPessoa':
        if PessoaFisica.is_pessoa_fisica(usuario):
            return UsuarioGenericoPessoaFisica.from_usuario(usuario)
        return UsuarioGenericoPessoaJuridica.from_usuario(usuario)

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[Pessoa]:
        return Pessoa

    def clean(self):
        UsuarioGenericoSimple.clean(self)
        self.TIPO_PESSOA.clean(self)

    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True


class UsuarioGenericoPessoaFisicaQuerySet(UsuarioGenericoPessoaQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {'cpf': F('codigo'), 'scope': F('pessoa_usuario__scope')}

    @CachedClassProperty
    def _aliased_fields(cls):
        return (
            super()._aliased_fields
            | UsuarioGenericoPessoaFisicaQuerySet._annotated_fields
        )

    def _complete(self):
        return super()._complete()

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'nome', 'sobrenome', 'data_nascimento', 'cpf'
        )


class UsuarioGenericoPessoaFisicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaFisicaQuerySet(
            self.model, using=self._db
        ).complete()

    def criar_usuario(
        self,
        cpf: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return super().criar_usuario(
            codigo=cpf,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )

    def criar_superusuario(
        self,
        cpf: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return super().criar_superusuario(
            codigo=cpf,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )


class UsuarioGenericoPessoaFisica(UsuarioGenericoPessoa, PessoaFisica):
    usuarios = UsuarioGenericoPessoaFisicaManager()

    @classmethod
    def from_usuario(
        cls, usuario: AbstractUsuarioGenerico
    ) -> 'UsuarioGenericoPessoaFisica':
        if not PessoaFisica.is_pessoa_fisica(usuario) or not hasattr(
            usuario, 'usuariogenericopessoafisica'
        ):
            raise TypeError(
                f'O usuário não pode ser convertido pois a pessoa '
                f'desse usuário não é uma pessoa física.'
            )
        return usuario.usuariogenericopessoafisica

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[PessoaFisica]:
        return PessoaFisica


class UsuarioGenericoPessoaJuridicaQuerySet(UsuarioGenericoPessoaQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {'cnpj': F('codigo'), 'scope': F('pessoa_usuario__scope')}

    @CachedClassProperty
    def _aliased_fields(cls):
        return (
            super()._aliased_fields
            | UsuarioGenericoPessoaJuridicaQuerySet._annotated_fields
        )

    def _complete(self):
        return super()._complete()

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'razao_social', 'nome_fantasia', 'cnpj'
        )


class UsuarioGenericoPessoaJuridicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaJuridicaQuerySet(
            self.model, using=self._db
        ).complete()

    def criar_usuario(
        self,
        cnpj: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return super().criar_usuario(
            codigo=cnpj,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )

    def criar_superusuario(
        self,
        cnpj: str,
        scope: Scope = None,
        password: str = None,
        email: str = None,
        telefone: str = None,
        **dados_pessoa,
    ):
        return super().criar_superusuario(
            codigo=cnpj,
            scope=scope,
            password=password,
            email=email,
            telefone=telefone,
            **dados_pessoa,
        )

    def get_by_razao_social(self, razao_social: str, escopo: Scope = None):
        return super().get_by_natural_key(
            username=PessoaJuridica.pessoas.get_by_razao_social(razao_social),
            scope=escopo,
        )


class UsuarioGenericoPessoaJuridica(UsuarioGenericoPessoa, PessoaJuridica):
    usuarios = UsuarioGenericoPessoaJuridicaManager()

    @classmethod
    def from_usuario(
        cls, usuario: AbstractUsuarioGenerico
    ) -> 'UsuarioGenericoPessoaJuridica':
        if not PessoaJuridica.is_pessoa_juridica(usuario) or not hasattr(
            usuario, 'usuariogenericopessoajuridica'
        ):
            raise TypeError(
                f'O usuário não pode ser convertido pois a pessoa '
                f'desse usuário não é uma pessoa jurídica.'
            )
        return usuario.usuariogenericopessoajuridica

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[PessoaJuridica]:
        return PessoaJuridica
