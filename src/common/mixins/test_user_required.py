from django.test import TestCase
from django.contrib.auth import get_user_model

from common.data import DadosEmpresa
from saas.models import GerenteDeContratos, ClienteContratante

User = get_user_model()


class TestLoginRequiredMixin:
    def setUp(self):
        self.gerente = GerenteDeContratos.gerente.load()

        self.gerente_password = DadosEmpresa.SENHA_DEFAULT

        self.clientes_contratantes = []
        self.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='38638467199208',
                password='test135',
                email='cliente1@test.dev',
                razao_social='Vendas LTDA',
                nome_fantasia='Teste vendas',
            )
        )

        self.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='41384478645272',
                password='test135',
                email='cliente2@test.dev',
                razao_social='Vendas SA',
                nome_fantasia='Teste vendas 2',
            )
        )
        self.clientes_contratantes_password = 'test135'

    def login_gerente(self):
        from scope_auth.models import Scope

        return self.client.login(
            username=self.gerente.cnpj,
            password=self.gerente_password,
            scope=Scope.scopes.default_scope(),
        )

    def login_cliente(self, id):
        from scope_auth.models import Scope

        return self.client.login(
            username=self.clientes_contratantes[id].cnpj,
            password=self.clientes_contratantes_password,
            scope=Scope.scopes.default_scope(),
        )

    def test_login_required(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)
