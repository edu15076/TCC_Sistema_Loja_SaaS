from django.db import models


class Contrato(models.Model):
    nome = models.CharField(max_length=100)
    ativo = models.BooleanField(default=True)
    # periodicidade

    # Ao assinar
    # vigencia
    # ...
