from django.db import models
from django.db.models import F
from django.utils.translation import gettext_lazy as _

from .codigo_escopo_pair import CodigoScopePair


class PessoaManager(models.Manager):
    def annotated_with_codigo(self):
        return super().get_queryset().annotate(codigo=F('codigo_escopo_pair__codigo'),
                                               escopo=F('codigo_escopo_pair__scope'))


class Pessoa(models.Model):
    nome = models.CharField(_('First name'), max_length=150, blank=True)
    sobrenome = models.CharField(_('Last name'), max_length=150, blank=True)
    email = models.EmailField(_('Endereço de email'), blank=True)

    data_nascimento = models.DateField(_('Data de nascimento'), blank=True, null=True)
    telefone = models.CharField(_('Telefone'), max_length=15, blank=True,
                                null=True)

    codigo_escopo_pair = models.OneToOneField(
        CodigoScopePair, on_delete=models.CASCADE, unique=False, blank=True,
        verbose_name=_('Código')
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
        return self.codigo_escopo_pair.codigo

    @codigo.setter
    def codigo(self, codigo):
        self.codigo_escopo_pair.codigo = codigo

    @property
    def escopo(self):
        return self.codigo_escopo_pair.scope

    def save(self, *args, **kwargs):
        self.codigo_escopo_pair.save()
        super(Pessoa, self).save(*args, **kwargs)
