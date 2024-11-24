from django.db import models

class FluxoDeCaixa(models.Model):
    caixa = models.ForeignKey('Caixa', on_delete=models.CASCADE, related_name='fluxos')
    horario_aberto = models.DateTimeField()
    horario_fechado = models.DateTimeField()
    valor_em_caixa = models.FloatField()

    def __str__(self):
        return (f"Fluxo {self.caixa.numero_identificacao} | "
                f"Abertura: {self.horario_aberto} | Fechamento: {self.horario_fechado}")