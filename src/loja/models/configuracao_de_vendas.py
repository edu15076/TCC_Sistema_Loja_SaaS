from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from util.mixins import ValidateModelMixin
from loja.models import Loja

class ConfiguracaoDeVendasQuerySet(models.QuerySet):
    pass


class ConfiguracaoDeVendasManager(models.Manager):
    def get_queryset(self):
        return ConfiguracaoDeVendasQuerySet(self.model, using=self._db).all()
    

class ConfiguracaoDeVendas(ValidateModelMixin, models.Model):
    loja = models.OneToOneField(
        Loja, verbose_name=_('Loja'), on_delete=models.CASCADE, editable=False
    )
    limite_porcentagem_desconto_maximo = models.DecimalField(
        _('Desconto máximo'),
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[
            MinValueValidator(0, _('Desconto máximo não pode ser negativo.')),
            MaxValueValidator(100, _('Desconto máximo não pode ser maior que 100%.')),
        ],
    )

    configuracoes = ConfiguracaoDeVendasManager()

    @receiver(post_save, sender=Loja)
    def create_configuracao_de_vendas(sender, instance, created, **kwargs):
        if created:
            ConfiguracaoDeVendas.configuracoes.create(loja=instance)

    def desconto_valido(self, desconto: Decimal) -> bool:
        return 0 <= desconto <= self.limite_porcentagem_desconto_maximo
