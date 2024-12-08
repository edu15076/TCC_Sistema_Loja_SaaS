from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse

from common.models.periodo import Periodo
from loja.models import Produto, Promocao
from loja.tests.mixins import UsuarioScopeLojaTestMixin


class TestGestaoPromocoesProdutoCRUDView(UsuarioScopeLojaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        super()._populate()

    def setUp(self) -> None:
        self.client = Client()
        self._populate()
        return super().setUp()

    def _populate(self):
        self.produtos = [
            Produto.produtos.create(
                descricao='Produto 1',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            ),
            Produto.produtos.create(
                descricao='Produto 2',
                preco_de_venda=200,
                em_venda=True,
                codigo_de_barras='5678567890123',
                loja=self.lojas[1],
            ),
        ]

        self.periodos = [
            Periodo.periodos.create(
                numero_de_periodos=60,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.DIA,
            )
        ]

        self.promocoes = [
            Promocao.promocoes.create(
                descricao='Promoção 1',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=1),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            ),
            Promocao.promocoes.create(
                descricao='Promoção 2',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=400),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            ),
            Promocao.promocoes.create(
                descricao='Promoção 3',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=70),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            ),
            Promocao.promocoes.create(
                descricao='Promoção 4',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=10),
                periodo=self.periodos[0],
                loja=self.lojas[1],
            ),
        ]

        self.produtos[0].promocoes.add(self.promocoes[0], self.promocoes[2])

    def _get_url(self, scope_pk, produto):
        return reverse(
            'gerir_promocoes_produto',
            kwargs={'loja_scope': scope_pk, 'pk': produto.pk},
        )

    def test_get_produto(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        response = self.client.get(self._get_url(scope.pk, self.produtos[0]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'gestao_oferta_produtos/promocoes_por_produto.html'
        )
        self.assertIn('promocoes_por_produto_form', response.context)
        self.assertIn('preco_de_venda_form', response.context)
        self.assertIn('em_venda_form', response.context)
        self.assertIn('scope', response.context)
        self.assertEqual(response.context['scope'], self.lojas[0].scope)

        produto = self.produtos[0]
        produto_response = response.context['produto']
        self.assertEqual(produto, produto_response)
        self.assertListEqual(
            list(produto.promocoes.all()), list(produto_response.promocoes.all())
        )

    def test_post_editar_em_venda_produto(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {'em_venda': False, 'em_venda_submit': 'Salvar'}
        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        self.assertEqual(response.status_code, 200, response.content)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertFalse(produto.em_venda)
        self.assertEqual(produto, produto_response)

        data = {'em_venda': True, 'em_venda_submit': 'Salvar'}
        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertTrue(produto.em_venda)
        self.assertEqual(produto, produto_response)

    def test_post_editar_preco_de_venda_produto(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {'preco_de_venda': 150, 'preco_de_venda_submit': 'Salvar'}
        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        preco_de_venda_response = Decimal(response.json()['preco_de_venda'])

        self.assertEqual(preco_de_venda_response, 150)
        self.assertEqual(produto.preco_de_venda, preco_de_venda_response)

    def test_post_adicionar_promocoes_validas_produto(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {
            'promocoes': [self.promocoes[1].pk],
            'promocoes_por_produto_submit': 'Salvar',
        }
        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        self.assertEqual(response.status_code, 200, response.content)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto, produto_response)
        self.assertEqual(len(produto.promocoes.all()), 1)
        self.assertListEqual(
            list(produto.promocoes.all()), list(produto_response.promocoes.all())
        )
        self.assertIn(self.promocoes[1], produto.promocoes.all())

    def test_post_remover_promocoes_produto(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {
            'promocoes': [self.promocoes[0].pk],
            'promocoes_por_produto_submit': 'Salvar',
        }

        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        self.assertEqual(response.status_code, 200, response.content)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto, produto_response)
        self.assertEqual(len(produto.promocoes.all()), 1)
        self.assertIn('erros', response.context)

    def test_post_duplicar_promocao(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {
            'data_inicio': date.today() + timedelta(days=200),
            'promocao': self.promocoes[0].pk,
            'produtos': [p.pk for p in self.promocoes[0].produtos.all()],
            'duplicar_promocao_submit': 'Salvar',
        }

        response = self.client.post(
            self._get_url(scope.pk, self.produtos[0]), data=data
        )

        self.assertEqual(response.status_code, 200, response.content)

        promocao = self.promocoes[0]
        promocao_response = response.context['promocao']

        self.assertEqual(promocao.periodo, promocao_response.periodo)
        self.assertEqual(
            promocao.porcentagem_desconto, promocao_response.porcentagem_desconto
        )

        self.assertEqual(len(response.context['erros']), 0)


class TestGestaoProdutosPromocaoCRUDView(UsuarioScopeLojaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        super()._populate()

    def setUp(self) -> None:
        self.client = Client()
        self._populate()
        return super().setUp()

    def _populate(self):
        self.produtos = [
            Produto.produtos.create(
                descricao='Produto 1',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            ),
            Produto.produtos.create(
                descricao='Produto 2',
                preco_de_venda=200,
                em_venda=True,
                codigo_de_barras='5678567890123',
                loja=self.lojas[1],
            ),
            Produto.produtos.create(
                descricao='Produto 3',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            ),
            Produto.produtos.create(
                descricao='Produto 4',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            ),
            Produto.produtos.create(
                descricao='Produto 5',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            ),
        ]

        self.periodos = [
            Periodo.periodos.create(
                numero_de_periodos=60,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.DIA,
            )
        ]

        self.promocoes = [
            Promocao.promocoes.create(
                descricao='Promoção 1',
                porcentagem_desconto=10,
                data_inicio=date.today(),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            ),
            Promocao.promocoes.create(
                descricao='Promoção 2',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=400),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            ),
            Promocao.promocoes.create(
                descricao='Promoção 3',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=70),
                periodo=self.periodos[0],
                loja=self.lojas[1],
            ),
        ]

        self.promocoes[0].produtos.add(self.produtos[0], self.produtos[2])
        self.promocoes[1].produtos.add(self.produtos[3])

    def _get_url(self, scope_pk, promocoa):
        return reverse(
            'gerir_produtos_promocao',
            kwargs={'loja_scope': scope_pk, 'pk': promocoa.pk},
        )

    def test_get_promocao(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        response = self.client.get(self._get_url(scope.pk, self.promocoes[0]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, 'gestao_oferta_produtos/produtos_por_promocao.html'
        )
        self.assertIn('produtos', response.context)
        self.assertIn('produtos_por_promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('promocao', response.context)
        self.assertEqual(response.context['scope'], self.lojas[0].scope)

        promocao = self.promocoes[0]
        promocao_response = response.context['promocao']
        self.assertEqual(promocao, promocao_response)
        self.assertListEqual(
            list(promocao.produtos.all()), list(promocao_response.produtos.all())
        )

    def test_post_duplicar_promocao(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {
            'data_inicio': date.today() + timedelta(days=200),
            'produtos': [p.pk for p in self.promocoes[0].produtos.all()],
            'duplicar_promocao_submit': 'Salvar',
        }

        response = self.client.post(
            self._get_url(scope.pk, self.promocoes[0]), data=data
        )

        redirect_url = response.url.split('/')
        redirect_url.pop(-3)
        loja_scope, pk = map(int, redirect_url[-3:-1])

        self.assertEqual(response.status_code, 302, response.content)
        self.assertEqual(loja_scope, scope.pk)

        nova_promocao = Promocao.promocoes.get(pk=pk)
        promocao = Promocao.promocoes.get(pk=self.promocoes[0].pk)

        self.assertEqual(nova_promocao.data_inicio, data['data_inicio'])
        self.assertNotEqual(promocao.data_inicio, nova_promocao.data_inicio)

    def test_post_adicionar_produtos_promocao(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope
        data = {
            'produtos': [self.produtos[4].pk, self.produtos[0].pk, self.produtos[2].pk],
            'produtos_por_promocao_submit': 'Salvar',
        }

        response = self.client.post(
            self._get_url(scope.pk, self.promocoes[0]), data=data
        )

        self.assertEqual(response.status_code, 200, response.content)

        promocao = Promocao.promocoes.get(pk=self.promocoes[0].pk)
        promocao_response = response.context['promocao']

        self.assertEqual(promocao, promocao_response)
        self.assertEqual(promocao.produtos.all().count(), 3)
        self.assertIn(self.produtos[4], promocao.produtos.all())
        self.assertListEqual(
            list(promocao.produtos.all()), list(promocao_response.produtos.all())
        )
