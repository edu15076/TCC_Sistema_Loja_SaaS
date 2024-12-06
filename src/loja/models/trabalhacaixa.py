from django.db import models


class TrabalhaCaixa(models.Model):
    caixeiro = models.ForeignKey(
        'Caixeiro',
        on_delete=models.CASCADE,
        related_name='trabalhos'
    )
    caixa = models.ForeignKey(
        'Caixa',
        on_delete=models.CASCADE,
        related_name='trabalhos'
    )
    trabalho_por_dia = models.ForeignKey(
        'TrabalhoPorDia',
        on_delete=models.CASCADE,
        related_name='trabalhos'
    )

    def __str__(self):
        return f"{self.caixeiro} - Caixa {self.caixa.numero_identificacao}"
