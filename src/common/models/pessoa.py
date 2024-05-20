from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from ..validators import codigo_validator


class PessoaManager(models.Manager):
    pass


class Pessoa(models.Model):
    codigo = models.CharField(
        _('Código'), max_length=14, unique=True, primary_key=True, editable=False,
        db_column='codigo', validators=[codigo_validator]
    )

    pessoas = PessoaManager()

    def is_pessoa_fisica(self):
        return hasattr(self, 'pessoa_fisica')

    def is_pessoa_juridica(self):
        return hasattr(self, 'pessoa_juridica')

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


class PessoaFisicaQuerySet(models.QuerySet):
    def simple(self):
        return self.values('nome', 'sobrenome', 'data_nascimento', 'cpf')

    def complete(self):
        return self.annotate(cpf=F('pessoa__codigo'))


class PessoaFisicaManager(PessoaManager):
    def get_queryset(self):
        return PessoaFisicaQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()


class PessoaFisica(Pessoa):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='pessoa_fisica',
        db_column='cpf'
    )

    nome = models.CharField(_('Primeiro nome'), max_length=100, blank=True)
    sobrenome = models.CharField(_('Sobrenome'), max_length=100, blank=True)
    data_nascimento = models.DateField(_('Data de nascimento'), blank=True, null=True)

    pessoas = PessoaFisicaManager()

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
        if len(self.cpf) != 11:
            raise ValidationError('O codigo de PessoaFisica deve ser um cpf')


class PessoaJuridicaQuerySet(models.QuerySet):
    def complete(self):
        return self.annotate(cnpj=F('pessoa__codigo'))

    def simple(self):
        return self.values('razao_social', 'nome_fantasia', 'cnpj')


class PessoaJuridicaManager(PessoaManager):
    def get_queryset(self):
        return PessoaJuridicaQuerySet(self.model, using=self._db).complete()

    def simple(self):
        return self.get_queryset().simple()


class PessoaJuridica(Pessoa):
    pessoa = models.OneToOneField(
        Pessoa,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='pessoa_juridica',
        db_column='cnpj'
    )

    razao_social = models.CharField(_('Razão social'), max_length=100,
                                    blank=True)
    nome_fantasia = models.CharField(_('Nome fantasia'), max_length=100,
                                     blank=True)

    pessoas = PessoaJuridicaManager()

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
        if len(self.cnpj) != 14:
            raise ValidationError('O codigo de PessoaJuridica deve ser um cnpj')
