from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse

from common.models.periodo import Periodo
from common.models.scopes import LojaScope
from loja.models import Produto, Loja, Promocao


class TestGestaoPromocoesProdutoCRUDView(TestCase):
    def setUp(self):
        super().setUp()

        self.client = Client()
        self._populate()

    def _get_url(self, scope, produto):
        return reverse(
            'gestao_promocoes_produto', kwargs={'scope': scope, 'pk': produto.pk}
        )

    def _populate(self):
        self.lojas = [Loja.lojas.create(nome='Loja1'), Loja.lojas.create(nome='Loja2')]

        self.produtos = []
        self.produtos.append(
            Produto.produtos.create(
                descricao='Produto 1',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[0],
            )
        )
        self.produtos.append(
            Produto.produtos.create(
                descricao='Produto 2',
                preco_de_venda=200,
                em_venda=False,
                codigo_de_barras='5678567890123',
                loja=self.lojas[1],
            )
        )

        self.periodos = []
        self.periodos.append(
            Periodo.periodos.create(
                numero_de_periodos=60,
                unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.DIA,
            )
        )

        self.promocoes = []
        self.promocoes.append(
            Promocao.promocoes.create(
                descricao='Promoção 1',
                porcentagem_desconto=10,
                data_inicio=date.today(),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            )
        )
        self.promocoes.append(
            Promocao.promocoes.create(
                descricao='Promoção 2',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=400),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            )
        )
        self.promocoes.append(
            Promocao.promocoes.create(
                descricao='Promoção 3',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=70),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            )
        )

        self.promocoes.append(
            Promocao.promocoes.create(
                descricao='Promoção 4',
                porcentagem_desconto=10,
                data_inicio=date.today() + timedelta(days=10),
                periodo=self.periodos[0],
                loja=self.lojas[0],
            )
        )

        self.produtos[0].promocoes.add(self.promocoes[0])
        self.produtos[0].promocoes.add(self.promocoes[2])

    def test_get_produto(self):
        response = self.client.get(self._get_url(1, self.produtos[0]))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promocoes_por_produto.html')
        self.assertIn('promocoes_form', response.context)
        self.assertIn('preco_form', response.context)
        self.assertIn('em_venda_form', response.context)
        self.assertIn('scope', response.context)
        # self.assertEqual(response.context['scope'], self.lojas[0].scope)

        produto = self.produtos[0]
        produto_response = response.context['produto']
        self.assertEqual(produto, produto_response)
        self.assertListEqual(
            list(produto.promocoes.all()), list(produto_response.promocoes.all())
        )

    def test_post_editar_em_venda_produto(self):
        data = {'em_venda': False}
        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        self.assertEqual(response.status_code, 200)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertFalse(produto.em_venda)
        self.assertEqual(produto, produto_response)

        data = {'em_venda': True}
        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertTrue(produto.em_venda)
        self.assertEqual(produto, produto_response)

    def test_post_editar_preco_de_venda_produto(self):
        data = {'preco_de_venda': 150}
        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto.preco_de_venda, 150)
        self.assertEqual(produto, produto_response)

    def test_post_adcionar_promocoes_validas_produto(self):
        data = {'promocoes': [self.promocoes[1].pk]}
        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        self.assertEqual(response.status_code, 200, response.content)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto, produto_response)
        self.assertEqual(len(produto.promocoes.all()), 1)
        self.assertListEqual(
            list(produto.promocoes.all()), list(produto_response.promocoes.all())
        )
        self.assertIn(self.promocoes[1], produto.promocoes.all())

    def test_post_remover_promocoes_invalidas_produto(self):
        data = {'promocoes': [self.promocoes[0].pk, self.promocoes[3].pk]}

        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        self.assertEqual(response.status_code, 200, response.content)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto, produto_response)
        self.assertEqual(len(produto.promocoes.all()), 1)
        self.assertIn('erros', response.context)

    def test_post_duplicar_promocao(self):
        data = {
            'data_inicio': date.today() + timedelta(days=300),
            'promocao': self.promocoes[0].pk,
            'produtos': [p.pk for p in self.promocoes[0].produtos.all()],
        }

        response = self.client.post(self._get_url(1, self.produtos[0]), data=data)

        self.assertEqual(response.status_code, 200, response.content)

        promocao = self.promocoes[0]
        promocao_response = response.context['promocao']

        self.assertEqual(promocao.periodo, promocao_response.periodo)
        self.assertEqual(
            promocao.porcentagem_desconto, promocao_response.porcentagem_desconto
        )

        self.assertEqual(len(response.context['erros']), 0)
