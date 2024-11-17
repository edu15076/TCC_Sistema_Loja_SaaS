from dataclasses import dataclass

from django.contrib.auth.models import Group


@dataclass
class DadosPapeis:
    CLIENTE_CONTRATANTE = Group.objects.get(name='saas_clientes_contratantes').name
    GERENTE_DE_CONTRATOS = Group.objects.get(name='saas_gerente_de_contratos').name
