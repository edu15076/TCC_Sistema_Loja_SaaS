from django.db import models
from django.utils.timezone import now

from loja.models.fluxodecaixa import FluxoDeCaixa

class Caixa(models.Model):
    numero_identificacao = models.CharField(max_length=50, unique=True) 
    loja = models.ForeignKey('Loja', on_delete=models.CASCADE, related_name='caixas')
    horario_aberto = models.DateTimeField(null=True, blank=True)
    dinheiro_em_caixa = models.FloatField(default=0.0)  
    ativo = models.BooleanField(default=False) 

    def fechar_caixa(self):
        if not self.ativo:
            raise ValueError("Caixa já está fechado.")
        
        fluxo = FluxoDeCaixa.objects.create(
            caixa=self,
            horario_aberto=self.horario_aberto,
            horario_fechado=now(),
            valor_em_caixa=self.dinheiro_em_caixa
        )
        
        self.horario_aberto = None
        self.ativo = False
        self.save()

        return fluxo

    def movimentar_dinheiro_em_caixa(self, valor):
        if not self.ativo:
            raise ValueError("O caixa está fechado. Não é possível movimentar dinheiro.")
        
        self.dinheiro_em_caixa += valor
        self.save()

    def __str__(self):
        return f"Caixa {self.numero_identificacao} - {'Ativo' if self.ativo else 'Fechado'}"