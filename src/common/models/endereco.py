import re
from typing import Iterable
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured, ValidationError
from requests.exceptions import Timeout

from sistema_loja_saas.settings import CEP_SETTINGS
from common.cep_providers import BaseCEPProvider
from util.logging import Loggers


class Endereco(models.Model):
    cep = models.CharField(_('CEP'), max_length=8, editable=False)
    numero = models.PositiveIntegerField(_('Numero'), blank=False)
    complemento = models.CharField(_('Complemento'), blank=True)

    _complete_data = None

    def cep_exists(self) -> bool:
        """Retorna se o cep do modelo existe"""
        return self.get_full_dict() is not None

    def get_full_dict(self) -> dict[str, str]:
        """Retorna um dicionário com o endereço completo"""

        if self._complete_data is not None:
            return self._complete_data

        providers = self._get_installed_cep_providers()
        cep_data = None
        logger = Loggers.get_logger()

        for provider in providers:
            try:
                cep_data = provider.get_cep_data(self.cep)

                if cep_data is not None:
                    break
            except Timeout as e:
                cep_data = None
                logger.warning(_((
                    "Tempo limite da solicitação ao provedor "
                    f"{provider.provider_id} atingido."
                )))

        if cep_data is not None:
            cep_data['numero'] = self.numero
            cep_data['complemento'] = self.complemento

        self._complete_data = cep_data

        return cep_data

    def _get_installed_cep_providers(self) -> list[BaseCEPProvider]:
        providers_ids = set()
        providers = []

        for provider_name in CEP_SETTINGS['PROVIDERS']:
            provider_class = import_string(provider_name)
            provider = provider_class(CEP_SETTINGS['PROVIDERS_TIMEOUT'])

            if not issubclass(type(provider), BaseCEPProvider):
                raise ImproperlyConfigured(_((
                    f"Classe provedora de CEP {provider.__class__.__name__}"
                    " deve herdar de "
                    "'common.cep_providers.BaseCEPProvider'"
                )))

            if provider.provider_id is None:
                raise ImproperlyConfigured(_((
                    f"Classe provedora de CEP {provider.__class__.__name__}"
                    " deve conter o atributo 'provider_id' e ele"
                    " não deve ser None"
                )))

            if provider.provider_id in providers_ids:
                raise ImproperlyConfigured(_((
                            "Mais de um provedor configurado com o id"
                            f" {provider.provider_id}"
                )))

            providers.append(provider)
            providers_ids.add(provider.provider_id)

        return providers

    def clean(self):
        if not self.cep_exists():
            raise ValidationError(_(f"Para ser salvo, o cep {self.cep} deve existir"))

        self.cep = self._complete_data['cep']

        super().clean()

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def complete_data(self) -> dict[str, str]:
        if self._complete_data is None:
            return self.get_full_dict()
        else:
            return self._complete_data

    @property
    def uf(self):
        return self.complete_data['uf']

    @property
    def cidade(self):
        return self.complete_data['cidade']

    @property
    def bairro(self):
        return self.complete_data.get('bairro')

    @property
    def rua(self):
        return self.complete_data.get('rua')
