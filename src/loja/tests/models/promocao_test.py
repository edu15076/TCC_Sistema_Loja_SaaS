from datetime import date, datetime, timedelta
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from common.models.periodo import Periodo
from loja.models import Produto, Loja, ProdutoPorLote, Promocao


class PromocaoModelTest(TestCase):
    def setUp(self):
        self.loja = Loja.lojas.create(nome='Loja Teste')
        self.produto = Produto.produtos.create(
            descricao='Produto 1',
            preco_de_venda=Decimal('100.00'),
            codigo_de_barras='1234567890123',
            em_venda=True,
            loja=self.loja,
        )
        self.periodo = Periodo.periodos.create(
            unidades_de_tempo_por_periodo=Periodo.UnidadeDeTempo.MES,
            numero_de_periodos=1,
        )
        self.promocao = Promocao(
            porcentagem_desconto=20,
            data_inicio=date.today(),
            descricao='Promoção Teste',
            periodo=self.periodo,
            loja=self.loja,
        )
        self.promocao.save()
        self.promocao.produtos.add(self.produto)

    def test_promocao_criacao(self):
        self.assertEqual(self.promocao.porcentagem_desconto, 20)
        self.assertEqual(self.promocao.descricao, 'Promoção Teste')
        self.assertEqual(self.promocao.periodo, self.periodo)
        self.assertEqual(self.promocao.loja, self.loja)
        self.assertIn(self.produto, self.promocao.produtos.all())

    def test_promocao_validacao_unica(self):
        with self.assertRaises(ValidationError):
            outra_promocao = Promocao(
                porcentagem_desconto=30,
                data_inicio=date.today() + timedelta(days=1),
                descricao='Outra Promoção',
                periodo=self.periodo,
                loja=self.loja,
            )
            outra_promocao.save()
            outra_promocao.produtos.add(self.produto)
            outra_promocao.save()

        try:
            outra_promocao = Promocao(
                porcentagem_desconto=30,
                data_inicio=date.today() + timedelta(days=60),
                descricao='Outra Promoção',
                periodo=self.periodo,
                loja=self.loja,
            )
            outra_promocao.save()
            outra_promocao.produtos.add(self.produto)
            outra_promocao.save()
        except ValidationError as e:
            self.fail(f'Raise inesperado: {e.messages[0]}')

    def test_promocao_clonar(self):
        nova_data_inicio = date.today() + timedelta(days=1)
        nova_promocao = self.promocao.clonar_promocao(nova_data_inicio)
        self.assertEqual(
            nova_promocao.porcentagem_desconto, self.promocao.porcentagem_desconto
        )
        self.assertEqual(nova_promocao.descricao, self.promocao.descricao)
        self.assertEqual(nova_promocao.periodo, self.promocao.periodo)
        self.assertEqual(nova_promocao.loja, self.promocao.loja)
        self.assertEqual(nova_promocao.data_inicio, nova_data_inicio)

    def test_produto_promocao_por_data(self):
        promocao = self.produto.promocao_por_data(date.today())
        self.assertEqual(promocao, self.promocao)

    def test_produto_promocao_ativa(self):
        promocao = self.produto.promocao_ativa()
        self.assertEqual(promocao, self.promocao)
