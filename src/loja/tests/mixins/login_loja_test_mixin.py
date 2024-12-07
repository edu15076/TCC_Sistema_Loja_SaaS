from django.test import Client
from django.urls import reverse

from common.models.periodo import Periodo
from loja.models.funcionario import *
from loja.models import Loja
from saas.models import ClienteContratante
from saas.models.contrato import Contrato
from saas.models.contrato_assinado import ContratoAssinado


class UsuarioScopeLojaTestMixin:
    @classmethod
    def _populate(cls):
        cls.clientes_contratantes = []
        cls.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='38638467199208',
                password='test135',
                email='cliente1@test.dev',
                razao_social='Vendas LTDA',
                nome_fantasia='Teste vendas',
            )
        )
        cls.clientes_contratantes.append(
            ClienteContratante.contratantes.criar_usuario_contratacao(
                cnpj='41384478645272',
                password='test135',
                email='cliente2@test.dev',
                razao_social='Vendas SA',
                nome_fantasia='Teste vendas 2',
            )
        )

        cls.lojas = list(Loja.lojas.all())
        cls.lojas[0].nome = 'Loja 1'
        cls.lojas[0].save()
        cls.lojas[1].nome = 'Loja 2'
        cls.lojas[1].save()

        cls.contratos = []
        cls.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 1',
                ativo=True,
                valor_por_periodo=1000,
                telas_simultaneas=2,
                taxa_de_multa=10,
                tempo_maximo_de_atraso_em_dias=30,
                periodo=Periodo.periodos.create(
                    numero_de_periodos=2,
                    unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.ANO,
                ),
            )
        )
        cls.contratos.append(
            Contrato.contratos.create(
                descricao='Contrato 2',
                ativo=False,
                valor_por_periodo=500,
                telas_simultaneas=3,
                taxa_de_multa=15,
                tempo_maximo_de_atraso_em_dias=60,
                periodo=Periodo.periodos.create(
                    numero_de_periodos=2,
                    unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.ANO,
                ),
            )
        )

        cls.contratos_assinados = []
        cls.contratos_assinados.append(
            ContratoAssinado.objects.create(
                vigente=True,
                contrato=cls.contratos[0],
                cliente_contratante=cls.clientes_contratantes[0],
            )
        )
        cls.contratos_assinados.append(
            ContratoAssinado.objects.create(
                vigente=True,
                contrato=cls.contratos[1],
                cliente_contratante=cls.clientes_contratantes[1],
            )
        )

        cls.gerente_financeiro = []
        cls.gerente_financeiro.append(
            GerenteFinanceiro.gerentes_financeiros.criar_funcionario(
                cpf='55780441588',
                loja=cls.lojas[0],
                password='password123',
                email='gerente_financeiro1@loja1.com',
                telefone='1111111111',
                nome='Gerente',
                sobrenome='Financeiro1',
            )
        )
        cls.gerente_financeiro.append(
            GerenteFinanceiro.gerentes_financeiros.criar_funcionario(
                cpf='00872068544',
                loja=cls.lojas[1],
                password='password123',
                email='gerente_financeiro2@loja2.com',
                telefone='2222222222',
                nome='Gerente',
                sobrenome='Financeiro2',
            )
        )

        cls.vendedores = []
        cls.vendedores.append(
            Vendedor.vendedores.criar_funcionario(
                cpf='05278505605',
                loja=cls.lojas[0],
                password='password123',
                email='vendedor1@loja1.com',
                telefone='3333333333',
                nome='Vendedor',
                sobrenome='1',
            )
        )
        cls.vendedores.append(
            Vendedor.vendedores.criar_funcionario(
                cpf='15525905426',
                loja=cls.lojas[1],
                password='password123',
                email='vendedor2@loja2.com',
                telefone='4444444444',
                nome='Vendedor',
                sobrenome='2',
            )
        )

        cls.caixeiros = []
        cls.caixeiros.append(
            Caixeiro.caixeiros.criar_funcionario(
                cpf='45851556358',
                loja=cls.lojas[0],
                password='password123',
                email='caixeiro1@loja1.com',
                telefone='5555555555',
                nome='Caixeiro',
                sobrenome='1',
            )
        )
        cls.caixeiros.append(
            Caixeiro.caixeiros.criar_funcionario(
                cpf='48185047693',
                loja=cls.lojas[1],
                password='password123',
                email='caixeiro2@loja2.com',
                telefone='6666666666',
                nome='Caixeiro',
                sobrenome='2',
            )
        )

        cls.gerente_de_rh = []
        cls.gerente_de_rh.append(
            GerenteDeRH.gerentes_de_rh.criar_funcionario(
                cpf='03560563178',
                loja=cls.lojas[0],
                password='password123',
                email='gerente_rh1@loja1.com',
                telefone='7777777777',
                nome='Gerente',
                sobrenome='RH1',
            )
        )
        cls.gerente_de_rh.append(
            GerenteDeRH.gerentes_de_rh.criar_funcionario(
                cpf='83419521227',
                loja=cls.lojas[1],
                password='password123',
                email='gerente_rh2@loja2.com',
                telefone='8888888888',
                nome='Gerente',
                sobrenome='RH2',
            )
        )

        cls.gerentes_de_estoque = []
        cls.gerentes_de_estoque.append(
            GerenteDeEstoque.gerentes_de_estoque.criar_funcionario(
                cpf='97205784913',
                loja=cls.lojas[0],
                password='password123',
                email='gerente_estoque1@loja1.com',
                telefone='9999999999',
                nome='Gerente',
                sobrenome='Estoque1',
            )
        )
        cls.gerentes_de_estoque.append(
            GerenteDeEstoque.gerentes_de_estoque.criar_funcionario(
                cpf='44495964550',
                loja=cls.lojas[1],
                password='password123',
                email='gerente_estoque2@loja2.com',
                telefone='0000000000',
                nome='Gerente',
                sobrenome='Estoque2',
            )
        )

        cls.funcionarios = [
            *cls.gerente_financeiro,
            *cls.vendedores,
            *cls.caixeiros,
            *cls.gerente_de_rh,
            *cls.gerentes_de_estoque,
        ]

    @classmethod
    def _get_url(cls, scope):
        return reverse('gerir_oferta_produtos', kwargs={'loja_scope': scope})

    def _login(self, funcionario):
        return self.client.login(
            username=funcionario.cpf,
            password='password123',
            scope=funcionario.loja.scope,
        )
