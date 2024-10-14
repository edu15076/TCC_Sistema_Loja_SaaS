from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _
from django.db.models.functions import Length

from ..validators import (codigo_validator, PESSOA_FISICA_CODIGO_LEN,
                          PESSOA_JURIDICA_CODIGO_LEN)


models.CharField.register_lookup(Length, 'length')


__all__ = (
    'PessoaManager',
    'Pessoa',
    'PessoaFisicaQuerySet',
    'PessoaFisicaManager',
    'PessoaFisica',
    'PessoaJuridicaQuerySet',
    'PessoaJuridicaManager',
    'PessoaJuridica',
)


class PessoaManager(models.Manager):
    pass


class Pessoa(models.Model):
    codigo = models.CharField(
        _('Código'),
        max_length=max(PESSOA_JURIDICA_CODIGO_LEN, PESSOA_FISICA_CODIGO_LEN),
        db_column='codigo',
        validators=[codigo_validator]
    )

    telefone = models.CharField(_('Telefone'), max_length=15, blank=True,
                                null=True)
    email = models.EmailField(_('Endereço de email'), blank=True)

    pessoas = PessoaManager()

    def __repr__(self):
        return str(self.codigo)

    def __str__(self):
        return self.__repr__()

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_full_name(self):
        raise NotImplementedError('Subclass must implement this method')

    def get_short_name(self):
        raise NotImplementedError('Subclass must implement this method')

    class Meta:
        abstract = True


class PessoaFisicaQuerySet(models.QuerySet):
    def complete(self):
        return self.annotate(cpf=F('codigo'))

    def simple(self):
        return self.values('nome', 'sobrenome', 'data_nascimento', 'cpf')


class PessoaFisicaManager(PessoaManager):
    def get_queryset(self):
        return PessoaFisicaQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()


class PessoaFisica(Pessoa):
    nome = models.CharField(_('Primeiro nome'), max_length=100, blank=True)
    sobrenome = models.CharField(_('Sobrenome'), max_length=100, blank=True)
    data_nascimento = models.DateField(_('Data de nascimento'), blank=True, null=True)

    pessoas = PessoaFisicaManager()

    @classmethod
    def is_pessoa_fisica(cls, pessoa: Pessoa):
        return (hasattr(pessoa, 'codigo') and
                len(pessoa.codigo) == PESSOA_FISICA_CODIGO_LEN)

    @property
    def cpf(self) -> str:
        return self.codigo

    @cpf.setter
    def cpf(self, cpf: str):
        self.codigo = cpf

    def get_full_name(self):
        return f'{self.nome} {self.sobrenome}'.strip()

    def get_short_name(self):
        return self.nome

    def clean(self):
        if self.cpf and len(self.cpf) != PESSOA_FISICA_CODIGO_LEN:
            raise ValidationError('CPF inválido')

    class Meta:
        abstract = True


class PessoaJuridicaQuerySet(models.QuerySet):
    def complete(self):
        return self.annotate(cnpj=F('codigo'))

    def simple(self):
        return self.values('razao_social', 'nome_fantasia', 'cnpj')


class PessoaJuridicaManager(PessoaManager):
    def get_queryset(self):
        return PessoaJuridicaQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()

    def get_by_razao_social(self, razao_social):
        return self.get_queryset().get(razao_social=razao_social)


class PessoaJuridica(Pessoa):
    razao_social = models.CharField(_('Razão social'), max_length=100,
                                    blank=True, unique=True)
    nome_fantasia = models.CharField(_('Nome fantasia'), max_length=100,
                                     blank=True)

    pessoas = PessoaJuridicaManager()

    @classmethod
    def is_pessoa_juridica(cls, pessoa: Pessoa):
        return (hasattr(pessoa, 'codigo') and
                len(pessoa.codigo) == PESSOA_JURIDICA_CODIGO_LEN)

    @property
    def cnpj(self) -> str:
        return self.codigo

    @cnpj.setter
    def cnpj(self, cnpj: str):
        self.codigo = cnpj

    def get_full_name(self):
        return f'{self.razao_social} - {self.nome_fantasia}'.strip()

    def get_short_name(self):
        return self.nome_fantasia

    def clean(self):
        if self.cnpj and len(self.cnpj) != PESSOA_JURIDICA_CODIGO_LEN:
            raise ValidationError('CNPJ inválido')

    class Meta:
        abstract = True
