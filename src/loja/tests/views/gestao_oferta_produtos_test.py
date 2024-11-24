from django.test import TestCase, Client
from django.urls import reverse

from common.models.scopes import LojaScope
from loja.models import Produto, Loja, ProdutoPorLote


class TestGestaoOfertaProdutoListView(TestCase):
    # TODO Testar acesso indevido
    def setUp(self):
        super().setUp()

        self.client = Client()
        self._populate()

    def _get_url(self, scope):
        return reverse('gestao_oferta_produtos', kwargs={'scope': scope})

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
                loja=self.lojas[0],
            )
        )

        self.produtos.append(
            Produto.produtos.create(
                descricao='Produto 3',
                preco_de_venda=100,
                em_venda=True,
                codigo_de_barras='1234567890123',
                loja=self.lojas[1],
            )
        )
        self.produtos.append(
            Produto.produtos.create(
                descricao='Produto 4',
                preco_de_venda=200,
                em_venda=False,
                codigo_de_barras='5678567890123',
                loja=self.lojas[1],
            )
        )

    def test_get(self):
        response = self.client.get(self._get_url(1))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'oferta_produtos.html')
        self.assertIn('form', response.context)
        self.assertIn('filter_form', response.context)
        self.assertIn('produtos', response.context)
        self.assertIn('scope', response.context)
        # todo self.assertEqual(response.context['scope'], self.lojas[0].scope)

        # self.assertEqual(
        #     response.context['produtos_count'],
        #     Produto.produtos.filter(loja=self.lojas[0]).count()
        # )

    def test_get_filter_em_venda(self):
        filter_data = {'em_venda': True, 'ordem': 'id'}

        response = self.client.get(self._get_url(1), data=filter_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'oferta_produtos.html')
        self.assertIn('form', response.context)
        self.assertIn('filter_form', response.context)
        self.assertIn('produtos', response.context)
        self.assertIn('scope', response.context)

        for produto in response.context['produtos']:
            self.assertTrue(produto.em_venda)

        filter_data = {'em_venda': False, 'ordem': 'id'}

        response = self.client.get(self._get_url(1), data=filter_data)

        for produto in response.context['produtos']:
            self.assertFalse(produto.em_venda)

    def test_get_order_produtos_preco_de_venda(self):
        filter_data = {'em_venda': '', 'ordem': '-preco_de_venda'}
        response = self.client.get(self._get_url(1), data=filter_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'oferta_produtos.html')
        self.assertIn('preco_form', response.context)
        self.assertIn('em_venda_form', response.context)
        self.assertIn('filter_form', response.context)
        self.assertIn('produtos', response.context)
        self.assertIn('scope', response.context)

        produtos_response = response.context['produtos']
        # todo produtos = Produto.produtos.filter(loja=self.lojas[0]).order_by('-preco_de_venda')
        produtos = Produto.produtos.all().order_by('-preco_de_venda')

        self.assertCountEqual(produtos_response, produtos)
        self.assertListEqual(list(produtos_response), list(produtos))

        filter_data = {'em_venda': '', 'ordem': 'preco_de_venda'}
        response = self.client.get(self._get_url(1), data=filter_data)

        produtos_response = response.context['produtos']
        produtos = produtos.order_by('preco_de_venda')

        self.assertCountEqual(produtos_response, produtos)
        self.assertListEqual(list(produtos_response), list(produtos))

    def test_post_pesquisar_produtos(self):
        query_data = {'query': '2'}
        response = self.client.post(self._get_url(1), data=query_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('produtos', response.context)

        produtos_response = response.context['produtos']
        produtos = Produto.produtos.all().filter(descricao__icontains='2')

        self.assertCountEqual(produtos_response, produtos)
        self.assertListEqual(list(produtos_response), list(produtos))

    def test_post_editar_preco_de_venda_produtos(self):
        data = {
            'pk': self.produtos[0].pk,
            'preco_de_venda': 150,
        }
        response = self.client.post(self._get_url(1), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('produto', response.context)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertEqual(produto.preco_de_venda, 150)
        self.assertEqual(produto, produto_response)

        data = {
            'preco_de_venda': 150,
        }
        response = self.client.post(self._get_url(1), data=data)

        self.assertEqual(response.status_code, 400)

        data = {
            'pk': self.produtos[0].pk,
            'preco_de_venda': -150,
        }
        response = self.client.post(self._get_url(1), data=data)

        self.assertEqual(response.status_code, 400)

    def test_post_editar_em_venda_produtos(self):
        data = {'pk': self.produtos[0].pk, 'em_venda': False}
        response = self.client.post(
            self._get_url(1) + '?visualizacao=tabela', data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('produto', response.context)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        produto_response = response.context['produto']

        self.assertFalse(produto.em_venda)
        self.assertEqual(produto, produto_response)

        data = {'pk': self.produtos[0].pk, 'em_venda': True}
        response = self.client.post(self._get_url(1), data=data)

        self.assertEqual(response.status_code, 200)

        produto = Produto.produtos.get(pk=self.produtos[0].pk)
        self.assertTrue(produto.em_venda)
