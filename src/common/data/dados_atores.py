from dataclasses import dataclass

from django.contrib.auth.models import Group

@dataclass
class DadosPapeis:
    CLIENTE_CONTRATANTE = 'saas_clientes_contratantes'
    GERENTE_DE_CONTRATOS = 'saas_gerente_de_contratos'
