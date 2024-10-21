from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator, MinLengthValidator

from saas.models.contrato import Contrato
from saas.models.usuario_contratacao import ClienteContratante

__all__ = [

]


class ContratoAssinadoQuerySet(models.QuerySet):
    pass


class ContratoAssinadoManager(models.Manager):
    def get_queryset(self):
        return ContratoAssinadoQuerySet(self.model, using==self._db).all()
    

class ContratoAssinado(models.Model):
    vigente = models.BooleanField(_('Assinatura vigente'), default=False)
    data_contratacao = models.DateField(
        _('Data da contratação'), 
        auto_now=False, 
        auto_now_add=True
    )
    contrato = models.ForeignKey(Contrato, on_delete=models.RESTRICT)
    cliente_contratante = models.ForeignKey(ClienteContratante, on_delete=models.RESTRICT)


    contratos_assinados = ContratoAssinadoManager()