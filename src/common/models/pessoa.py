from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from .codigo_escopo_pair import CodigoEscopoPair


class PessoaManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().annotate(codigo=F('username__codigo'),
                                               escopo=F('username__escopo'))


class Pessoa(models.Model):
    nome = models.CharField(_('First name'), max_length=150, blank=True)
    sobrenome = models.CharField(_('Last name'), max_length=150, blank=True)
    email = models.EmailField(_('Endereço de email'), blank=True)

    data_nascimento = models.DateField(_('Data de nascimento'), blank=True, null=True)
    telefone = models.CharField(_('Telefone'), max_length=15, blank=True,
                                null=True)

    username = models.OneToOneField(
        CodigoEscopoPair, on_delete=models.CASCADE, unique=True, blank=True,
        verbose_name=_('ID do pair de código e escopo')
    )

    pessoas = PessoaManager()

    @property
    def nome_completo(self):
        return f'{self.nome} {self.sobrenome}'.strip()

    @property
    def primeiro_nome(self):
        return self.nome

    @property
    def codigo(self):
        return self.username.codigo

    @codigo.setter
    def codigo(self, codigo):
        self.username.codigo = codigo

    @property
    def escopo(self):
        return self.username.escopo

    def save(self, *args, **kwargs):
        self.username.save()
        super(Pessoa, self).save(*args, **kwargs)
