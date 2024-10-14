from typing import ClassVar
import pandas as pd
from dataclasses import dataclass
from unidecode import unidecode
import re
from pathlib import Path

from util.decorators import CachedClassProperty

__all__ = ('DadosEmpresa',)


class _DadosEmpresaMeta(type):
    @CachedClassProperty
    def _dados_empresa(cls) -> dict:
        src_path = next((parent
                         for parent in Path(__file__).parents
                         if parent.name == 'src'), None)
        return cls._parse_dados_empresa(src_path / 'empresa.csv')

    @classmethod
    def _parse_dados_empresa(cls, dados_empresa_path: Path) -> dict[str, str]:
        with open(dados_empresa_path, 'r', encoding='utf-8') as dados_empresa_file:
            df = pd.read_csv(dados_empresa_file, encoding='utf-8')
            dados_empresa_dirty: dict[str, str] = df.to_dict('records')[0]

            # transforma as chaves para uppercase
            dados_empresa: dict[str, str] = {
                unidecode(
                    key.strip().upper().replace(' ', '_')
                ): str(dados_empresa_dirty[key])
                for key in dados_empresa_dirty
            }

            # limpa o cnpj
            dados_empresa['CNPJ'] = re.sub(r'\D', '', dados_empresa['CNPJ'])

            # todas as validações necessárias ocorrem na criação no bd

            return dados_empresa

    def __getattr__(self, item):
        return self._dados_empresa[item]


class _DadosEmpresa(metaclass=_DadosEmpresaMeta):
    """
    Permite o acesso aos atributos:

    `RAZAO_SOCIAL`, `NOME_FANTASIA`, `CNPJ`, `SENHA_DEFAULT`, `TELEFONE`, `EMAIL`,
    `EMAIL_TECNICO`, `EMAIL_PAGAMENTO`
    """
    pass


@dataclass
class DadosEmpresa:
    RAZAO_SOCIAL: ClassVar[str] = _DadosEmpresa.RAZAO_SOCIAL
    NOME_FANTASIA: ClassVar[str] = _DadosEmpresa.NOME_FANTASIA
    CNPJ: ClassVar[str] = _DadosEmpresa.CNPJ
    SENHA_DEFAULT: ClassVar[str] = _DadosEmpresa.SENHA_DEFAULT
    TELEFONE: ClassVar[str] = _DadosEmpresa.TELEFONE
    EMAIL: ClassVar[str] = _DadosEmpresa.EMAIL
    EMAIL_TECNICO: ClassVar[str] = _DadosEmpresa.EMAIL_TECNICO
    EMAIL_PAGAMENTO: ClassVar[str] = _DadosEmpresa.EMAIL_PAGAMENTO
