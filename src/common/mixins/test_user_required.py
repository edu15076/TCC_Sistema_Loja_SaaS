from django.test import TestCase
from django.contrib.auth import get_user_model

from common.data import DadosEmpresa
from saas.models import GerenteDeContratos, ClienteContratante

User = get_user_model()

class TestLoginRequiredMixin(TestCase):
    def setUp(self):
        try:
            self.gerente = GerenteDeContratos.gerente.criar_usuario_contratacao(
                cnpj='34561499177486', 
                password='usuariodeTeste', 
                email='gerente@test.dev', 
            )
        except:
            self.gerente = GerenteDeContratos.gerente.load()

        self.gerente_password = 'usuariodeTeste'

        self.clientes_contratantes = []
        self.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='38638467199208', 
                password='test135', 
                email='cliente1@test.dev', 
                razao_social='Vendas LTDA', 
                nome_fantasia='Teste vendas'
            )
        )

        self.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='41384478645272', 
                password='test135', 
                email='cliente2@test.dev', 
                razao_social='Vendas SA', 
                nome_fantasia='Teste vendas 2'
            )
        )
        self.clientes_contratantes_password = 'test135'

    def login(self, user, password: str):
        self.client.login(username=user.cnpj, password=password)

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
    