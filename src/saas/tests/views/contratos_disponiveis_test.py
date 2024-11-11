from django.test import TestCase, Client
from django.urls import reverse

from saas.models import Contrato
from common.models import Periodo
from saas.views import ContratosDisponiveisCRUDView


class TestContratosDisponiveisCRUDView(ContratosDisponiveisCRUDView, TestCase):
    def setUp(self):
        super().setUp()

        self.client = Client()
        self.url = reverse('contratos_disponiveis')

        self.periodos = []
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=2, 
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.ANO
            )
        )
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=6, 
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.MES
            )
        )
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=7, 
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.DIA
            )
        )

        self.contratos = []
        self.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 1', 
                ativo=True, 
                valor_por_periodo=1000, 
                telas_simultaneas=2, 
                taxa_de_multa=10, 
                tempo_maximo_de_atraso_em_dias=30, 
                periodo=self.periodos[0]
            )
        )
        self.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 2', 
                ativo=False, 
                valor_por_periodo=2000, 
                telas_simultaneas=3, 
                taxa_de_multa=15, 
                tempo_maximo_de_atraso_em_dias=60, 
                periodo=self.periodos[1]
            )
        )
        self.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 3', 
                ativo=True, 
                valor_por_periodo=3000, 
                telas_simultaneas=4, 
                taxa_de_multa=20, 
                tempo_maximo_de_atraso_em_dias=90, 
                periodo=self.periodos[2]
            )
        )

    def test_lista_contratos(self):
        response = self.client.get(self.url)
        print(response.context)