from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.forms.models import model_to_dict

from saas.models import Contrato
from common.models import Periodo
from saas.views import GestaoContratoCRUDListView
from common.mixins import TestLoginRequiredMixin


class TestGestaoContratoCRUDListView(TestLoginRequiredMixin, TestCase):
    multi_db = True

    def setUp(self):
        super().setUp()

        self.client = Client()
        self.url = reverse('gestao_contrato')

        self.periodos = []
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=2,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.ANO,
            )
        )
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=6,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.MES,
            )
        )
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=7,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.DIA,
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
                periodo=self.periodos[0],
            )
        )
        self.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 2', 
                ativo=False, 
                valor_por_periodo=500, 
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
                periodo=self.periodos[2],
            )
        )

    def test_acesso_cliente(self):
        self.login_cliente(0)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    def test_get_contratos(self):
        self.login_gerente()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('form', response.context)
        self.assertIn('filter_form', response.context)
        self.assertIn('contratos', response.context)

    def test_get_filter_contratos_ativos(self):
        self.login_gerente()

        data = {
            'ativo':True,
            'ordem':'id'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])

        contratos_ativos = Contrato.contratos.filter(ativo=True).order_by('id')

        self.assertCountEqual(contratos_ativos, contratos_response)
        self.assertListEqual(list(contratos_ativos), contratos_response)

    def test_get_filter_contratos_inativos(self):
        self.login_gerente()

        data = {
            'ativo':False,
            'ordem':'id'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])

        contratos_inativos = Contrato.contratos.filter(ativo=False).order_by('id')

        self.assertCountEqual(contratos_inativos, contratos_response)
        self.assertListEqual(list(contratos_inativos), contratos_response)

    def test_get_order_valor_por_periodo(self):
        self.login_gerente()

        data = {
            'ativo': 'todos',
            'ordem': 'valor_por_periodo'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])

        contratos = Contrato.contratos.order_by('valor_por_periodo')

        self.assertCountEqual(contratos, contratos_response)
        self.assertListEqual(list(contratos), contratos_response)

    def test_get_order_valor_por_periodo_decrescente(self):
        self.login_gerente()

        data = {
            'ativo': 'todos',
            'ordem': '-valor_por_periodo'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])
        
        contratos = Contrato.contratos.order_by('-valor_por_periodo')
        
        self.assertCountEqual(contratos, contratos_response)
        self.assertListEqual(list(contratos), contratos_response)

    def test_get_order_valor_valor_total(self):
        self.login_gerente()

        data = {
            'ativo': 'todos',
            'ordem': 'valor_total'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])
        contratos = Contrato.contratos.order_by('valor_total')

        self.assertCountEqual(contratos, contratos_response)
        self.assertListEqual(list(contratos), contratos_response)

    def test_get_order_valor_total_decrescente(self):
        self.login_gerente()

        data = {
            'ativo': 'todos',
            'ordem': '-valor_total'
        }

        response = self.client.get(self.url, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('filter_form', response.context)
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)

        contratos_response = list(response.context['contratos'])
        
        contratos = Contrato.contratos.order_by('-valor_total')
        
        self.assertCountEqual(contratos, contratos_response)
        self.assertListEqual(list(contratos), contratos_response)

    def test_post_criar_contrato(self):
        self.login_gerente()

        data = {
            'descricao': 'Novo Contrato',
            'ativo': True,
            'valor_por_periodo': 4000,
            'telas_simultaneas': 5,
            'taxa_de_multa': 25,
            'tempo_maximo_de_atraso_em_dias': 120,
            'unidades_de_tempo_por_periodo': Periodo.UnidadeDeTempo.MES,
            'numero_de_periodos': 12,
        }

        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contrato.contratos.filter(descricao='Novo Contrato').exists())

        novo_contrato_response = response.context['contrato']
        novo_contrato_response_dict = model_to_dict(novo_contrato_response)
        novo_contrato_response_dict['valor_por_periodo'] = Decimal(novo_contrato_response.valor_por_periodo)
        novo_contrato_response_dict['valor_total'] = Decimal(novo_contrato_response.valor_total)

        novo_contrato = Contrato.contratos.get(descricao='Novo Contrato')
        novo_contrato_dict = model_to_dict(novo_contrato)
        novo_contrato_dict['valor_por_periodo'] = Decimal(novo_contrato.valor_por_periodo)
        novo_contrato_dict['valor_total'] = Decimal(novo_contrato.valor_total)
                                                                       

        self.assertDictEqual(novo_contrato_dict, novo_contrato_response_dict)

        fail_data = {
            'descricao': 'Novo Contrato',
            'ativo': True,
            'valor_por_periodo': 4000,
            'telas_simultaneas': 5,
            'taxa_de_multa': 25,
            'tempo_maximo_de_atraso_em_dias': 120,
            'numero_de_periodos': 12,
        }

        fail_response = self.client.post(self.url, fail_data)
        self.assertNotEqual(fail_response.status_code, 200)

    def test_post_ativar_contrato(self):
        self.login_gerente()

        data = {
            'id': self.contratos[1].id
        }

        response = self.client.post(f"{self.url}", data=data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contrato.contratos.get(id=self.contratos[1].id).ativo)

        data = {
            'id': 'inexistente'
        }

        response = self.client.post(f"{self.url}", data=data)
        self.assertEqual(response.status_code, 400)

    def test_post_desativar_contrato(self):
        self.login_gerente()

        data = {
            'id': self.contratos[0].id
        }

        response = self.client.post(f"{self.url}", data=data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contrato.contratos.get(id=self.contratos[0].id).ativo)

        data = {
            'id': 'inexistente'
        }

        response = self.client.post(f"{self.url}", data=data)
        self.assertEqual(response.status_code, 400)
