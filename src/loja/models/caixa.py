from django.db import models
from django.utils import timezone

from loja.models.fluxodecaixa import FluxoDeCaixa

class CaixaQuerySet(models.QuerySet):
    pass


class CaixaManager(models.Manager):
    def get_queryset(self):
        return CaixaQuerySet(self.model, using=self._db).all()
    
class Caixa(models.Model):
    numero_identificacao = models.CharField(max_length=50, unique=True)
    loja = models.ForeignKey('Loja', on_delete=models.CASCADE, related_name='caixas')
    horario_aberto = models.DateTimeField(null=True, blank=True)  
    dinheiro_em_caixa = models.FloatField(default=0.0)
    ativo = models.BooleanField(default=True)  

    @property
    def is_open(self):
        return self.horario_aberto is not None
    
    @is_open.setter
    def is_open(self, value):
        self.horario_aberto = timezone.now() if value else None

    def fechar_caixa(self):
        if not self.is_open:
            raise ValueError("Caixa já está fechado.")

        fluxo = FluxoDeCaixa.objects.create(
            caixa=self,
            horario_aberto=self.horario_aberto,
            horario_fechado=timezone.now(),
            valor_em_caixa=self.dinheiro_em_caixa
        )

        self.horario_aberto = None
        self.save()
        return fluxo

    def movimentar_dinheiro_em_caixa(self, valor):
        if not self.is_open:
            raise ValueError("O caixa está fechado. Não é possível movimentar dinheiro.")

        if self.dinheiro_em_caixa + valor < 0:
            raise ValueError("Valor a ser retirado é maior que o disponível em caixa.")
        self.dinheiro_em_caixa += valor
        self.save()

    def __str__(self):
        return f"Caixa {self.numero_identificacao} - {'Aberto' if self.is_open else 'Fechado'}"

    class Meta:
        permissions = [
            ("manage_caixa", "Pode gerenciar caixas"),
        ]