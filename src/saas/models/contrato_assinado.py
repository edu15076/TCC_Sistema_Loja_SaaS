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
    # Aqui você pode adicionar métodos personalizados para filtrar os contratos assinados
    pass


class ContratoAssinadoManager(models.Manager):
    def get_queryset(self):
        return ContratoAssinadoQuerySet(self.model, using=self._db)

    def contratos_disponiveis(self):
        """
        Retorna contratos que estão disponíveis para assinatura.
        """
        return self.get_queryset().filter(vigente=True)


class ContratoAssinado(models.Model):
    vigente = models.BooleanField(_('Assinatura vigente'), default=False)
    data_contratacao = models.DateField(
        _('Data da contratação'),
        auto_now_add=True  # Apenas define na criação
    )
    contrato = models.ForeignKey(Contrato, on_delete=models.RESTRICT)
    cliente_contratante = models.ForeignKey(ClienteContratante, on_delete=models.RESTRICT)

    # Gerenciador personalizado
    objects = ContratoAssinadoManager()

    def values_visualizacao_cliente_contratante(self) -> dict:
        """
        Retorna um dicionário com os valores calculados ou atributos do contrato
        para visualização no cliente contratante.
        """
        return {
            'data_contratacao': self.data_contratacao,
            'contrato': self.contrato.descricao,
            'valor_por_periodo': float(self.contrato.valor_por_periodo),
            'telas_simultaneas': self.contrato.telas_simultaneas,
            'taxa_de_multa': self.contrato.taxa_de_multa,
            'tempo_maximo_de_atraso_em_dias': self.contrato.tempo_maximo_de_atraso_em_dias,
            'valor_total': float(self.contrato.valor_total),
            'periodo': self.contrato.periodo.tempo_total.days,  # Ajuste conforme necessário
        }

    def calcular_multa(self, valor_por_periodo: float, taxa_de_multa: float, total_periodos: int) -> float:
        """
        Calcula a multa restante para o cliente contratante com base no tempo restante.
        """
        dias_passados = (date.today() - self.data_contratacao).days
        # Total de períodos decorridos desde a contratação
        periodos_decorridos = dias_passados // total_periodos
        periodos_restantes = total_periodos - periodos_decorridos

        if periodos_restantes <= 0:
            return 0  # Nenhuma multa se o contrato já terminou
        
        valor_restante = periodos_restantes * valor_por_periodo
        valor_multa = valor_restante * taxa_de_multa
        
        return valor_multa
