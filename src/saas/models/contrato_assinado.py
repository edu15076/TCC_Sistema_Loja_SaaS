from django.db import models
from django.utils.translation import gettext_lazy as _

from datetime import date
from saas.models.contrato import Contrato
from saas.models.usuario_contratacao import ClienteContratante

__all__ = [
    'ContratoAssinadoQuerySet',
    'ContratoAssinadoManager',
    'ContratoAssinado',
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

    def values_visualizacao_cliente_contratante(self) -> dict:
        return {
            'data_contratacao': self.data_contratacao,
            'contrato': self.contrato.values_visualizacao_cliente_contratante(),
            # TODO: Colocar os restos dos atributos relevantes e atributos calculados
        }
    
    def calcular_multa(self) -> float:
        dias_passados = (date.today() - self.data_contratacao).days
        periodos_decorridos = dias_passados // self.periodo.numero_de_periodos
        periodos_restantes = self.total_periodos - periodos_decorridos

        if periodos_restantes <= 0:
            return 0  
        
        valor_restante = periodos_restantes * self.valor_por_periodo
        valor_multa = valor_restante * self.taxa_de_multa
        
        return valor_multa