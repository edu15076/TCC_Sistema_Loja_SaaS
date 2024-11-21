from datetime import datetime
from decimal import Decimal

from django.test import TestCase

from common.models.scopes import LojaScope
from loja.models import Produto, Loja, ProdutoPorLote


class ProdutoModelTest(TestCase):
    def setUp(self):
        self.loja = Loja.lojas.create(nome='Loja Teste')
        self.produto = Produto.produtos.create(
            descricao='Produto 1',
            preco_de_venda=Decimal('100.00'),
            codigo_de_barras='1234567890123',
            em_venda=True,
            loja=self.loja,
        )
        self.produto_por_lote = ProdutoPorLote.produtos_por_lote.create(
            lote='Lote 1', qtd_em_estoque=10, produto=self.produto
        )

    def test_produto_criacao(self):
        self.assertEqual(self.produto.preco_de_venda, Decimal('100.00'))
        self.assertEqual(self.produto.codigo_de_barras, '1234567890123')
        self.assertTrue(self.produto.em_venda)
        self.assertEqual(self.produto.loja, self.loja)

    def test_produto_qtd_em_estoque(self):
        self.assertEqual(self.produto.qtd_em_estoque, 10)

    def test_produto_promocao_por_data(self):
        promocao = self.produto.promocao_por_data(datetime.now())
        self.assertIsNone(promocao)

    def test_produto_promocao_ativa(self):
        promocao = self.produto.promocao_ativa()
        self.assertIsNone(promocao)

    def test_produto_por_lote_criacao(self):
        self.assertEqual(self.produto_por_lote.lote, 'Lote 1')
        self.assertEqual(self.produto_por_lote.qtd_em_estoque, 10)
        self.assertEqual(self.produto_por_lote.produto, self.produto)
