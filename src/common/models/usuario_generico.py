from datetime import date

from django.contrib.postgres.aggregates import ArrayAgg
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from scope_auth.models import (Scope, AbstractUserPerScopeWithEmail,
                               UserPerScopeWhitEmailManager)
from util.decorators import CachedClassProperty, CachedProperty
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
    def filter_pessoas_fisicas(self):
        """Filtra usuários que são pessoas físicas."""
        return self.filter(
            pessoa_usuario__pessoa__pessoa_fisica__isnull=False
        )

    def as_usuarios_pessoa_fisica(self):
        self.__class__ = UsuarioGenericoPessoaFisicaQuerySet
        self.model = UsuarioGenericoPessoaFisica
        return self.complete()

    def filter_pessoas_juridicas(self):
        """Filtra usuários que são pessoas jurídicas."""
        return self.filter(
            pessoa_usuario__pessoa__pessoa_juridica__isnull=False
        )

    def as_usuarios_pessoa_juridica(self):
        self.__class__ = UsuarioGenericoPessoaJuridicaQuerySet
        self.model = UsuarioGenericoPessoaJuridica
        return self.complete()

    def usuarios_per_scope(self):
        return self.values(scope='pessoa_usuario__scope').annotate(
            pessoas=ArrayAgg('pessoa_usuario__pessoa')
        )

    def complete(self):
        return self.select_related('pessoa_usuario', 'pessoa_usuario__pessoa',
                                   'pessoa_usuario__pessoa__pessoa_juridica',
                                   'pessoa_usuario__pessoa__pessoa_fisica')


class UsuarioGenericoManager(UserPerScopeWhitEmailManager):
    def get_queryset(self):
        return UsuarioGenericoQuerySet(self.model, using=self._db).complete()

    def get_by_codigo(self, codigo: str, escopo: Scope = None):
        return super().get_by_natural_key(username=Pessoa.pessoas.get(codigo=codigo),
                                          scope=escopo)


class AbstractUsuarioGenerico(AbstractUserPerScopeWithEmail):
    pessoa_usuario = models.OneToOneField(
        PessoaUsuario, on_delete=models.CASCADE, verbose_name=_('Código'),
        related_name='usuario', editable=False, unique=True
    )
    telefone = models.CharField(_('Telefone'), max_length=15, blank=True,
                                null=True)
    email = models.EmailField(_('Endereço de email'), blank=True)

    usuarios = UsuarioGenericoManager()

    USERNAME_PER_SCOPE_FIELD = 'pessoa_usuario'

    class Meta:
        abstract = True

    @property
    def pessoa(self):
        return self.pessoa_usuario.pessoa

    @pessoa.setter
    def pessoa(self, pessoa):
        self.pessoa_usuario.pessoa = cast_to_model(pessoa, Pessoa)

    def as_usuario_pessoa_fisica(self):
        if not self.pessoa.is_pessoa_fisica():
            raise TypeError(f'O usuário não pode ser convertido pois a pessoa '
                            f'{self.pessoa.codigo} não é uma pessoa física.')
        self.__class__ = UsuarioGenericoPessoaFisica
        return self

    def as_usuario_pessoa_juridica(self):
        if not self.pessoa.is_pessoa_juridica():
            raise TypeError(f'O usuário não pode ser convertido pois a pessoa '
                            f'{self.pessoa.codigo} não é uma pessoa jurídica.')
        self.__class__ = UsuarioGenericoPessoaJuridica
        return self

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        if self.pessoa.is_pessoa_fisica():
            return self.pessoa.pessoa_fisica.get_full_name()
        else:
            return self.pessoa.pessoa_juridica.get_full_name()

    def get_short_name(self):
        """Return the short name for the user."""
        if self.pessoa.is_pessoa_fisica():
            return self.pessoa.pessoa_fisica.get_short_name()
        else:
            return self.pessoa.pessoa_juridica.get_short_name()

    def enviar_email_para_usuario(self, subject, message, from_email=None, **kwargs):
        """Envia um email para esse usuário."""
        self.email_user(subject, message, from_email, **kwargs)

    def __repr__(self):
        return (f'<UsuarioGenerico: {{codigo={self.pessoa.codigo}, '
                f'scope={self.pessoa_usuario.scope}}}>')

    def __str__(self):
        return repr(self)

    def clean(self):
        self.pessoa.clean()
        super().clean()

    def clean_fields(self, exclude=None):
        self.pessoa.clean_fields(exclude)
        super().clean()


class UsuarioGenerico(AbstractUsuarioGenerico):
    pass


class UsuarioGenericoSimpleQuerySet(UsuarioGenericoQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {
            'pessoa': F('pessoa_usuario__pessoa'),
            'scope': F('pessoa_usuario__scope')
        }

    @CachedClassProperty
    def _aliased_fields(cls):
        return UsuarioGenericoSimpleQuerySet._annotated_fields

    def _complete(self):
        return self.alias(**self._aliased_fields)

    def complete(self):
        return super().complete()._complete().annotate(**self._annotated_fields)

    def simple(self):
        return self.values('telefone', 'email', 'pessoa', 'scope')


class UsuarioGenericoSimpleManager(UsuarioGenericoManager):
    def get_queryset(self):
        return UsuarioGenericoSimpleQuerySet(self.model, using=self._db).complete()

    def from_usuarios_queryset(self, qs):
        qs.__class__ = UsuarioGenericoSimpleQuerySet
        qs.model = UsuarioGenericoSimple
        return qs.complete()

    def simple(self):
        return self.get_queryset().simple()


class UsuarioGenericoSimple(UsuarioGenerico):
    usuarios = UsuarioGenericoSimpleManager()

    @classmethod
    def from_usuario(cls, usuario):
        usuario.__class__ = UsuarioGenericoSimple
        return usuario

    @property
    def scope(self) -> Scope:
        return self.pessoa_usuario.scope

    @scope.setter
    def scope(self, scope: Scope):
        self.pessoa_usuario.scope = cast_to_model(scope, Scope)

    def save(self, *args, **kwargs):
        self.pessoa_usuario.save()
        super().save(*args, **kwargs)

    class Meta:
        proxy = True


class UsuarioGenericoPessoaQuerySet(UsuarioGenericoSimpleQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {
            'codigo': F('pessoa_usuario__pessoa__codigo'),
            'scope': F('pessoa_usuario__scope'),
            'pessoa': F('pessoa_usuario__pessoa')
        }

    @CachedClassProperty
    def _aliased_fields(cls):
        return super()._aliased_fields | UsuarioGenericoPessoaQuerySet._annotated_fields

    def simple(self):
        return self.values('telefone', 'email', 'scope', 'codigo')


class UsuarioGenericoPessoaManager(UsuarioGenericoSimpleManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaQuerySet(
            self.model, using=self._db).complete()

    def from_usuarios_queryset(self, qs):
        qs.__class__ = UsuarioGenericoPessoaQuerySet
        qs.model = UsuarioGenericoPessoa
        return qs.complete()

    def _criar_pessoa(self, codigo: str, **dados_pessoa):
        self.model.TIPO_PESSOA._meta.default_manager.get_or_create(
            codigo=codigo, **dados_pessoa)

    def criar_usuario(
            self, codigo: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        self._criar_pessoa(codigo, **dados_pessoa)
        return self.create_user_by_natural_key(
            pessoa=codigo, scope=scope, password=password, email=email,
            telefone=telefone
        )

    def criar_superusuario(
            self, codigo: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        self._criar_pessoa(codigo, **dados_pessoa)
        return self.create_superuser_by_natural_key(
            pessoa=codigo, scope=scope, password=password, email=email,
            telefone=telefone
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
    def from_usuario(cls, usuario):
        usuario.__class__ = UsuarioGenericoPessoa
        return usuario

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[Pessoa]:
        return Pessoa

    @property
    def codigo(self) -> str:
        return self.pessoa.codigo

    @codigo.setter
    def codigo(self, codigo: str):
        self.pessoa.codigo = codigo

    def save(self, *args, **kwargs):
        self.pessoa.save()
        return super().save(*args, **kwargs)

    class Meta:
        proxy = True


class UsuarioGenericoPessoaFisicaQuerySet(UsuarioGenericoPessoaQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {
            'pessoa': F('pessoa_usuario__pessoa__pessoa_fisica'),
            'nome': F('pessoa_usuario__pessoa__pessoa_fisica__nome'),
            'sobrenome': F('pessoa_usuario__pessoa__pessoa_fisica__sobrenome'),
            'data_nascimento': F('pessoa_usuario__pessoa__pessoa_fisica__'
                                 'data_nascimento'),
            'cpf': F('pessoa_usuario__pessoa__codigo'),
            'scope': F('pessoa_usuario__scope')
        }

    @CachedClassProperty
    def _aliased_fields(cls):
        return (super()._aliased_fields |
                UsuarioGenericoPessoaFisicaQuerySet._annotated_fields)

    def _complete(self):
        return super()._complete().filter_pessoas_fisicas()

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'nome', 'sobrenome', 'data_nascimento', 'cpf'
        )


class UsuarioGenericoPessoaFisicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaFisicaQuerySet(
            self.model, using=self._db).complete()

    def from_usuarios_queryset(self, qs):
        qs.__class__ = UsuarioGenericoPessoaFisicaQuerySet
        qs.model = UsuarioGenericoPessoaFisica
        return qs.complete()

    def criar_usuario(
            self, cpf: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        return super().criar_usuario(
            codigo=cpf, scope=scope, password=password, email=email, telefone=telefone,
            **dados_pessoa
        )

    def criar_superusuario(
            self, cpf: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        return super().criar_superusuario(
            codigo=cpf, scope=scope, password=password, email=email, telefone=telefone,
            **dados_pessoa
        )


class UsuarioGenericoPessoaFisica(UsuarioGenericoPessoa):
    usuarios = UsuarioGenericoPessoaFisicaManager()

    @classmethod
    def from_usuario(cls, usuario):
        if not usuario.pessoa.is_pessoa_fisica():
            raise ValueError('Usuário não é pessoa física.')
        usuario.__class__ = UsuarioGenericoPessoaFisica
        return usuario

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[PessoaFisica]:
        return PessoaFisica

    @property
    def pessoa(self) -> PessoaFisica:
        return super().pessoa.pessoa_fisica

    @pessoa.setter
    def pessoa(self, pessoa):
        self.pessoa_usuario.pessoa = cast_to_model(pessoa, Pessoa)

    @property
    def nome(self) -> str:
        return self.pessoa.nome

    @nome.setter
    def nome(self, nome: str):
        self.pessoa.nome = nome

    @property
    def sobrenome(self) -> str:
        return self.pessoa.sobrenome

    @sobrenome.setter
    def sobrenome(self, sobrenome: str):
        self.pessoa.sobrenome = sobrenome

    @property
    def data_nascimento(self) -> date:
        return self.pessoa.data_nascimento

    @data_nascimento.setter
    def data_nascimento(self, data_nascimento: date):
        self.pessoa.data_nascimento = data_nascimento

    @property
    def cpf(self) -> str:
        return self.pessoa.cpf

    @cpf.setter
    def cpf(self, cpf: str):
        self.pessoa.cpf = cpf

    class Meta:
        proxy = True


class UsuarioGenericoPessoaJuridicaQuerySet(UsuarioGenericoPessoaQuerySet):
    @CachedClassProperty
    def _annotated_fields(cls):
        return {
            'pessoa': F('pessoa_usuario__pessoa__pessoa_juridica'),
            'razao_social': F('pessoa_usuario__pessoa__pessoa_juridica__razao_social'),
            'nome_fantasia': F('pessoa_usuario__pessoa__pessoa_juridica__nome_fantasia'),
            'cnpj': F('pessoa_usuario__pessoa__codigo'),
            'scope': F('pessoa_usuario__scope')
        }

    @CachedClassProperty
    def _aliased_fields(cls):
        return (super()._aliased_fields |
                UsuarioGenericoPessoaJuridicaQuerySet._annotated_fields)

    def _complete(self):
        return super()._complete().filter_pessoas_juridicas()

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'razao_social', 'nome_fantasia', 'cnpj'
        )


class UsuarioGenericoPessoaJuridicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaJuridicaQuerySet(
            self.model, using=self._db).complete()

    def from_usuarios_queryset(self, qs):
        qs.__class__ = UsuarioGenericoPessoaJuridicaQuerySet
        qs.model = UsuarioGenericoPessoaJuridica
        return qs.complete()

    def criar_usuario(
            self, cnpj: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        return super().criar_usuario(
            codigo=cnpj, scope=scope, password=password, email=email, telefone=telefone,
            **dados_pessoa
        )

    def criar_superusuario(
            self, cnpj: str, scope: Scope = None, password: str = None,
            email: str = None, telefone: str = None, **dados_pessoa
    ):
        return super().criar_superusuario(
            codigo=cnpj, scope=scope, password=password, email=email, telefone=telefone,
            **dados_pessoa
        )


class UsuarioGenericoPessoaJuridica(UsuarioGenericoPessoa):
    usuarios = UsuarioGenericoPessoaJuridicaManager()

    @classmethod
    def from_usuario(cls, usuario):
        if not usuario.pessoa.is_pessoa_juridica():
            raise ValueError('Usuário não é pessoa jurídica.')
        usuario.__class__ = UsuarioGenericoPessoaJuridica
        return usuario

    @CachedClassProperty
    def TIPO_PESSOA(self) -> type[PessoaJuridica]:
        return PessoaJuridica

    @property
    def pessoa(self) -> PessoaJuridica:
        return super().pessoa.pessoa_juridica

    @pessoa.setter
    def pessoa(self, pessoa):
        self.pessoa_usuario.pessoa = cast_to_model(pessoa, Pessoa)

    @property
    def razao_social(self) -> str:
        return self.pessoa.razao_social

    @razao_social.setter
    def razao_social(self, razao_social: str):
        self.pessoa.razao_social = razao_social

    @property
    def nome_fantasia(self) -> str:
        return self.pessoa.nome_fantasia

    @nome_fantasia.setter
    def nome_fantasia(self, nome_fantasia: str):
        self.pessoa.nome_fantasia = nome_fantasia

    @property
    def cnpj(self) -> str:
        return self.pessoa.cnpj

    @cnpj.setter
    def cnpj(self, cnpj: str):
        self.pessoa.cnpj = cnpj

    class Meta:
        proxy = True
