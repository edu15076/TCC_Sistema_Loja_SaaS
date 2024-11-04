from django.test import TestCase, Client
from django.urls import reverse
from django.core.management import call_command
from django.http import JsonResponse

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

    def test_acesso_nao_autenticado(self):
        pass

    def test_get_contratos(self):
        self.login_gerente()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'lista_contratos.html')
        self.assertIn('form', response.context)
        self.assertIn('contratos', response.context)



    def test_get_filter_contratos_ativos(self):
        pass

    def test_get_filter_contratos_inativos(self):
        pass

    def test_get_order_valor_por_periodo(self):
        pass

    def test_get_order_valor_total(self):
        pass

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
            'numero_de_periodos': 12
        }


        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contrato.contratos.filter(descricao='Novo Contrato').exists())

        novo_contrato = response.json()['data']
        novo_contrato_dict = response.json()['data']
        novo_contrato_dict['periodo_id'] = novo_contrato_dict['periodo']
        del novo_contrato_dict['periodo']
        print(Contrato.contratos.filter(descricao='Novo Contrato').values())
        print(novo_contrato_dict)
        # novo_contrato_dict['tempo_maximo_de_atraso_em_dias'] = novo_contrato.periodo.numero_de_periodos
        # novo_contrato_dict['unidades_de_tempo_por_periodo'] = novo_contrato.periodo.unidades_de_tempo_por_periodo

        self.assertDictEqual(data, novo_contrato_dict)

        fail_data = {
            'descricao': 'Novo Contrato',
            'ativo': True,
            'valor_por_periodo': 4000,
            'telas_simultaneas': 5,
            'taxa_de_multa': 25,
            'tempo_maximo_de_atraso_em_dias': 120,
            'numero_de_periodos': 12
        }

        fail_response = self.client.post(self.url, fail_data)
        self.assertNotEqual(fail_response.status_code, 200)

    def test_post_atualizar_contrato(self):
        pass

    def test_post_ativar_contrato(self):
        self.login_gerente()

        data = {
            'operacao': 'ativar_contrato',
            'id': self.contratos[1].id
        }

        response = self.client.post(f"{self.url}{data['id']}/", data)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Contrato.contratos.get(id=self.contratos[1].id).ativo)

        data = {
            'operacao': 'ativar_contrato',
            'id': 'inexistente'
        }

        response = self.client.post(f"{self.url}{data['id']}/", data)
        self.assertEqual(response.status_code, 404)

    def test_post_desativar_contrato(self):
        self.login_gerente()

        data = {
            'operacao': 'desativar_contrato',
            'id': self.contratos[1].id
        }

        response = self.client.post(f"{self.url}{data['id']}/", data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Contrato.contratos.get(id=self.contratos[1].id).ativo)

        data = {
            'operacao': 'desativar_contrato',
            'id': 'inexistente'
        }

        response = self.client.post(f"{self.url}{data['id']}/", data)
        self.assertEqual(response.status_code, 404)

    def test_post_view(self):
        pass
        # data = {
        #     # Preencha com os dados necessários para criar um contrato
        #     'campo1': 'novo_valor1',
        #     'campo2': 'novo_valor2',
        # }
        # response = self.client.post(self.url, data)
        # self.assertEqual(response.status_code, 302)  # Verifica se redireciona após o POST
        # self.assertTrue(Contrato.objects.filter(campo1='novo_valor1').exists())

    def test_delete_contratos(self):
        pass
        # delete_url = reverse('nome_da_sua_view_delete', args=[self.contrato.id])  # Ajuste para a URL de delete
        # response = self.client.delete(delete_url)
        # self.assertEqual(response.status_code, 204)
        # self.assertFalse(Contrato.objects.filter(id=self.contrato.id).exists())