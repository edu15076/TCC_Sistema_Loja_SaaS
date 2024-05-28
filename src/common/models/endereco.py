from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.module_loading import import_string
from django.core.exceptions import ImproperlyConfigured
from requests.exceptions import Timeout

from util.mixins import ValidateModelMixin, NotUpdatableFieldMixin
from sistema_loja_saas.settings import CEP_SETTINGS
from common.cep_providers import BaseCEPProvider
from util.logging import Loggers
from common.validators import CEPValidator


class EnderecoManager(models.Manager):
    @classmethod
    def get_installed_cep_providers(cls) -> list[BaseCEPProvider]:
        """
        :return: instancias dos provedores de CEP configurados
        :rtype: list[BaseCEPProvider]
        """

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


class Endereco(NotUpdatableFieldMixin, ValidateModelMixin, models.Model):
    cep = models.CharField(_('CEP'), max_length=8, validators=[CEPValidator(EnderecoManager().get_installed_cep_providers)])
    numero = models.PositiveIntegerField(_('Numero'), blank=False)
    complemento = models.CharField(_('Complemento'), blank=True)

    _complete_data = None
    not_updatable_fields = ['cep']

    enderecos = EnderecoManager()
    objects = models.Manager()

    def cep_exists(self) -> bool:
        """Retorna se o cep do modelo existe"""
        cache = Endereco.enderecos.filter(cep=self.cep).exists()
        return cache or self.get_full_dict() is not None

    def get_full_dict(self) -> dict[str, str]:
        """Retorna um dicionário com o endereço completo"""

        if self._complete_data is not None:
            self._complete_data['numero'] = self.numero
            self._complete_data['complemento'] = self.complemento
            return self._complete_data

        providers = Endereco.enderecos.get_installed_cep_providers()
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
            cep_data['id'] = self.id
            cep_data['numero'] = self.numero
            cep_data['complemento'] = self.complemento

        self._complete_data = cep_data

        return cep_data

    @property
    def complete_data(self) -> dict[str, str]:
        if self._complete_data is None:
            return self.get_full_dict()
        else:
            return self._complete_data

    @property
    def uf(self):
        return self.complete_data.get('uf')

    @property
    def cidade(self):
        return self.complete_data.get('cidade')

    @property
    def bairro(self):
        return self.complete_data.get('bairro')

    @property
    def rua(self):
        return self.complete_data.get('rua')


