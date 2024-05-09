from django.db import models
from django.db.models import Q

from .util import SingletonModel
from ..util.annotations import ClassProperty
from ..util.annotations.cached_property import CachedProperty


class EscopoManager(models.Manager):
    pass


class Escopo(models.Model):
    @property
    def eh_escopo_de_contratacao(self):
        return self.id == EscopoContratacao.instance_id


class EscopoContratacaoManager(EscopoManager):
    use_in_migrations = True

    @property
    def instance_id(self):
        return 1

    @CachedProperty
    def instance(self):
        return self.get(id=self.instance_id)


class EscopoContratacao(Escopo, SingletonModel):
    escopo_contratacao = EscopoContratacaoManager()

    @ClassProperty
    def instance_id(self):
        return self.escopo_contratacao.instance_id

    @ClassProperty
    def instance(self):
        return self.escopo_contratacao.instance


class EscopoLojaManager(EscopoManager):
    def get_queryset(self):
        return super().get_queryset().filter(~Q(id=EscopoContratacao.instance_id))


class EscopoLoja(Escopo):
    """
    Define o escopo de cada loja a partir do segundo Escopo.
    """

    class Meta:
        abstract = True
