from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator


class CaixaQuerySet(models.QuerySet):
    pass


class CaixaManager(models.Manager):
    def get_queryset(self):
        return CaixaQuerySet(self.model, using=self._db).all()


class Caixa(models.Model):
    numero_identificacao_validator = RegexValidator(
        regex=r'^\d{8}$',
        message="O número de identificação deve ter exatamente 8 dígitos.",
        code='invalid_numero_identificacao'
    )

    numero_identificacao = models.CharField(
        max_length=8,
        validators=[numero_identificacao_validator],
    )

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

    def movimentar_dinheiro_em_caixa(self, valor):
        if not self.is_open:
            raise ValueError(
                "O caixa está fechado. Não é possível movimentar dinheiro.")

        if self.dinheiro_em_caixa + valor < 0:
            raise ValueError("Valor a ser retirado é maior que o disponível em caixa.")
        self.dinheiro_em_caixa += valor
        self.save()

    def __str__(self):
        return (f"Caixa {self.numero_identificacao} - "
                f"{'Aberto' if self.is_open else 'Fechado'}")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['numero_identificacao', 'loja'],
                                    name='unique_caixa_per_loja')
        ]
