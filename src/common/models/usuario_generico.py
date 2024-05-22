from datetime import date

from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from scope_auth.models import (Scope, AbstractUserPerScopeWithEmail,
                               UserPerScopeWhitEmailManager)
from util.decorators import CachedClassProperty
from util.models import cast_to_model
from .pessoa import PessoaFisica, PessoaJuridica, Pessoa

from .pessoa_usuario import PessoaUsuario


class UsuarioGenericoQuerySet(models.QuerySet):
    def filter_pessoas_fisicas(self):
        """Filtra usuários que são pessoas físicas."""
        return self.filter(
            pessoa_usuario__pessoa__pessoa_fisica__isnull=False
        )

    def as_usuarios_pessoa_fisica(self):
        qs = self.filter_pessoas_fisicas()
        qs.__class__ = UsuarioGenericoPessoaFisicaQuerySet
        qs.model = UsuarioGenericoPessoaFisica
        return qs.complete()

    def filter_pessoas_juridicas(self):
        """Filtra usuários que são pessoas jurídicas."""
        return self.filter(
            pessoa_usuario__pessoa__pessoa_juridica__isnull=False
        )

    def as_usuarios_pessoa_juridica(self):
        qs = self.filter_pessoas_juridicas()
        qs.__class__ = UsuarioGenericoPessoaJuridicaQuerySet
        qs.model = UsuarioGenericoPessoaJuridica
        return qs.complete()

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
        return self.pessoa_usuario.pessoa.get_full_name()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.pessoa_usuario.pessoa.get_short_name()

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
    def complete(self):
        return super().complete().annotate(pessoa=F('pessoa_usuario__pessoa'),
                                           scope=F('pessoa_usuario__scope'))

    def simple(self):
        return self.values('telefone', 'email', 'pessoa', 'scope')


class UsuarioGenericoSimpleManager(UsuarioGenericoManager):
    def get_queryset(self):
        return UsuarioGenericoSimpleQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()


class UsuarioGenericoSimple(UsuarioGenerico):
    usuarios = UsuarioGenericoSimpleManager()

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
    def complete(self):
        return super().complete().annotate(codigo=F('pessoa_usuario__pessoa__codigo'))

    def simple(self):
        return self.values('telefone', 'email', 'scope', 'codigo')


class UsuarioGenericoPessoaManager(UsuarioGenericoSimpleManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaQuerySet(
            self.model, using=self._db).complete()

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
    def complete(self):
        return super().complete().filter_pessoas_fisicas().annotate(
            pessoa_fisica=F('pessoa_usuario__pessoa__pessoa_fisica'),
            nome=F('pessoa_usuario__pessoa__pessoa_fisica__nome'),
            sobrenome=F('pessoa_usuario__pessoa__pessoa_fisica__sobrenome'),
            data_nascimento=F('pessoa_usuario__pessoa__pessoa_fisica__data_nascimento'),
            cpf=F('codigo')
        )

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'nome', 'sobrenome', 'data_nascimento', 'cpf'
        )


class UsuarioGenericoPessoaFisicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaFisicaQuerySet(
            self.model, using=self._db).complete()

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
    def complete(self):
        return super().complete().filter_pessoas_juridicas().annotate(
            pessoa_juridica=F('pessoa_usuario__pessoa__pessoa_juridica'),
            razao_social=F('pessoa_usuario__pessoa__pessoa_juridica__razao_social'),
            nome_fantasia=F('pessoa_usuario__pessoa__pessoa_juridica__nome_fantasia'),
            cnpj=F('codigo')
        )

    def simple(self):
        return self.values(
            'telefone', 'email', 'scope', 'razao_social', 'nome_fantasia', 'cnpj'
        )


class UsuarioGenericoPessoaJuridicaManager(UsuarioGenericoPessoaManager):
    def get_queryset(self):
        return UsuarioGenericoPessoaJuridicaQuerySet(
            self.model, using=self._db).complete()

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
