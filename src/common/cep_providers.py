from abc import ABC, abstractmethod
import re

from requests import Request, Session


class BaseCEPProvider(ABC):
    provider_id = None

    def __init__(self, timeout: float = None):
        self.timeout = timeout

    def request(
        self, url, method='GET', data=None, response_encoding="utf-8", headers=None
    ):
        s = Session()
        req = Request(method, url, data=data, headers=headers or {})

        prepped = req.prepare()

        resp = s.send(prepped, timeout=self.timeout)

        if response_encoding:
            resp.encoding = response_encoding

        return resp.json()

    def clean_cep(self, cep: str) -> str:
        """Remove hifens do cep"""
        match = re.match(r"^(\d{5})-?(\d{3})$", cep)
        return "".join(match.groups())

    def _clean_street(self, street: str | None = None):
        """
        Remove numeros da rua e outras informações retornando apenas a rua.
        """

        if street is not None:
            match = re.match(r"^([^,]+),?\s(\d+|s/n)$", street)
            if match is not None:
                return match.groups()[0]
            return street

    def _extract_district(self, original_fields: dict):
        """
        Extrai o nome da cidade e do bairro.
        """

        fields = original_fields.copy()
        if fields.get("bairro") is None:
            match = re.match(r"^(.+)\s\((.+)\)$", fields["cidade"])

            if match:
                district, city = match.groups()
                fields["bairro"] = district
                fields["cidade"] = city

        return fields

    @abstractmethod
    def clean(self, raw_fields: dict, cep: str) -> dict:
        """Retorna um dicionário tratado do endereço completo

        :param raw_fields: um dicionário com o endereço
        :type raw_fields: dict
        :param cep: valor do cep
        :type cep: str
        :return: o endereço tratado
        :rtype: dict
        """

    @abstractmethod
    def get_cep_data(self, cep: str) -> dict:
        """Recupera o endereço completo

        :param cep: código do cep
        :type cep: str
        :return: dicionário contendo as chaves:
        - cep
        - uf
        - cidade
        - bairro
        - rua

        :rtype: dict
        """


class RepublicaVirtualCEPProvider(BaseCEPProvider):
    provider_id = 'replubica_virtual'

    def _get_url(self, cep: str) -> str:
        """Retorna a url com o ceo fornecido"""
        return f"http://cep.republicavirtual.com.br/web_cep.php?cep={self.clean_cep(cep)}&formato=json"

    def get_cep_data(self, cep: str) -> dict:
        raw_fields = self.request(
            self._get_url(cep), headers={"Accept": "application/json"}
        )

        if int(raw_fields['resultado']) > 0:
            return self.clean(raw_fields, cep)

        return None

    def _clean_state(self, state: str) -> str:
        return state.split(" ")[0].strip()

    def clean(self, raw_fields: dict, cep) -> dict:
        fields = {
            key: value.strip()
            for key, value in raw_fields.items()
            if value is not None and value.strip()
        }

        if 'logradouro' in fields and 'tipo_logradouro' in fields:
            fields['rua'] = f"{fields['tipo_logradouro']} {fields['logradouro']}"

        return {
            'cep': self.clean_cep(cep),
            'uf': self._clean_state(fields['uf']),
            'cidade': fields['cidade'],
            'bairro': fields.get('bairro'),
            'rua': fields.get('rua'),
        }
