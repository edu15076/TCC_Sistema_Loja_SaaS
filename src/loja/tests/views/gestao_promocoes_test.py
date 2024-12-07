from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.db.models import F

from common.models.periodo import Periodo
from common.models.scopes import LojaScope
from loja.models import Produto, Loja, Promocao
from loja.tests.mixins import UsuarioScopeLojaTestMixin


class TestGestaoPromocoesListView(UsuarioScopeLojaTestMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        super()._populate()

    def setUp(self):
        super().setUp()

        self.client = Client()
        self._populate()

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
                loja=self.lojas[0],
            ),
            Produto.produtos.create(
                descricao='Produto 2',
                preco_de_venda=200,
                em_venda=False,
                codigo_de_barras='5678567890123',
                loja=self.lojas[1],
            ),
        ]

        self.periodos = [
            Periodo.periodos.create(
                numero_de_periodos=30,
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

        self.produtos[0].promocoes.add(self.promocoes[0], self.promocoes[1])
        self.produtos[1].promocoes.add(self.promocoes[1])

    def _get_url(self, scope_pk, promocao_pk=None):
        if promocao_pk:
            return reverse(
                'gestao_promocao',
                kwargs={'loja_scope': scope_pk, 'promocao_pk': promocao_pk},
            )
        return reverse('gestao_promocoes', kwargs={'loja_scope': scope_pk})

    def test_get(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        response = self.client.get(self._get_url(scope.pk))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promocoes.html')
        self.assertIn('promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('filter_form', response.context)

        self.assertEqual(
            response.context['promocoes_count'],
            Promocao.promocoes.filter(loja=self.lojas[0]).count(),
        )

    def test_get_filter_status(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {'status': 1, 'ordem': 'id'}

        response = self.client.get(self._get_url(scope.pk), data)
        self.assertTemplateUsed(response, 'promocoes.html')
        self.assertIn('promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('filter_form', response.context)

        self.assertListEqual(
            list(
                Promocao.promocoes.filter(
                    loja=self.lojas[0],
                    data_inicio__gte=date.today()
                    - F('periodo__numero_de_periodos')
                    * F('periodo__unidades_de_tempo_por_periodo'),
                    data_inicio__lte=date.today(),
                )
            ),
            list(response.context['promocoes']),
        )

    def test_get_filter_produtos_presentes(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {'produtos': [self.produtos[1].pk], 'ordem': 'id'}

        response = self.client.get(self._get_url(scope.pk), data)
        self.assertTemplateUsed(response, 'promocoes.html')
        self.assertIn('promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('filter_form', response.context)

        self.assertListEqual(
            list(
                Promocao.promocoes.filter(loja=self.lojas[0], produtos=self.produtos[1])
            ),
            list(response.context['promocoes']),
        )

    def test_get_order_data_inicio_promocoes(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {'status': 0, 'ordem': '-data_inicio'}

        response = self.client.get(self._get_url(scope.pk), data)
        self.assertTemplateUsed(response, 'promocoes.html')
        self.assertIn('promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('filter_form', response.context)

        promocoes = Promocao.promocoes.filter(loja=self.lojas[0]).order_by(
            '-data_inicio'
        )
        self.assertListEqual(list(response.context['promocoes']), list(promocoes))

        data = {'status': 0, 'ordem': 'data_inicio'}
        response = self.client.get(self._get_url(scope.pk), data)

        promocoes = Promocao.promocoes.filter(loja=self.lojas[0]).order_by(
            'data_inicio'
        )
        self.assertListEqual(list(response.context['promocoes']), list(promocoes))

    def test_get_order_porcentagem_desconto_promocoes(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {'status': 0, 'ordem': '-porcentagem_desconto'}

        response = self.client.get(self._get_url(scope.pk), data)
        self.assertTemplateUsed(response, 'promocoes.html')
        self.assertIn('promocao_form', response.context)
        self.assertIn('duplicar_promocao_form', response.context)
        self.assertIn('filter_form', response.context)

        promocoes = Promocao.promocoes.filter(loja=self.lojas[0]).order_by(
            '-porcentagem_desconto'
        )
        self.assertListEqual(list(response.context['promocoes']), list(promocoes))

        data = {'status': 0, 'ordem': 'porcentagem_desconto'}
        response = self.client.get(self._get_url(scope.pk), data)

        promocoes = Promocao.promocoes.filter(loja=self.lojas[0]).order_by(
            'porcentagem_desconto'
        )
        self.assertListEqual(list(response.context['promocoes']), list(promocoes))

    def test_post_duplicar_promocoes(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {
            'promocao': self.promocoes[0].pk,
            'data_inicio': date.today() + timedelta(days=100),
            'produtos': [p.pk for p in self.promocoes[0].produtos.all()],
            'duplicar_promocao_submit': 'Duplicar',
        }

        response = self.client.post(self._get_url(scope.pk), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'linhas/linha_promocao.html')
        self.assertIn('promocao', response.context)

        self.assertEqual(data['data_inicio'], response.context['promocao'].data_inicio)
        self.assertListEqual(
            list(self.promocoes[0].produtos.all()),
            list(response.context['promocao'].produtos.all()),
        )

        data = {
            'promocao': self.promocoes[0].pk,
            'data_inicio': date.today() + timedelta(days=10),
            'produtos': [p.pk for p in self.promocoes[0].produtos.all()],
            'duplicar_promocao_submit': 'Duplicar',
        }

        response = self.client.post(
            f'{self._get_url(scope.pk)}{self.promocoes[0].pk}/', data=data
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            list(self.promocoes[0].produtos.all()),
            list(response.context['promocao'].produtos.all()),
        )

    def test_post_criar_promocao(self):
        self._login(self.gerente_financeiro[0])
        scope = self.gerente_financeiro[0].loja.scope

        data = {
            'descricao': 'Promoção 5',
            'porcentagem_desconto': 10,
            'data_inicio': date.today() + timedelta(days=50),
            'produtos': [self.produtos[0].pk],
            'unidades_de_tempo_por_periodo': Periodo.UnidadeDeTempo.DIA,
            'numero_de_periodos': 10,
            'promocao_submit': 'Salvar',
        }

        response = self.client.post(self._get_url(scope.pk), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'linhas/linha_promocao.html')
        self.assertIn('promocao', response.context)

        promocao = Promocao.promocoes.get(descricao='Promoção 5')
        self.assertEqual(promocao, response.context['promocao'])
        self.assertListEqual(
            list(response.context['promocao'].produtos.all()),
            list(promocao.produtos.all()),
        )

        data = {
            'descricao': 'Promoção 5',
            'porcentagem_desconto': 10,
            'data_inicio': date.today(),
            'produtos': [self.produtos[0].pk],
            'unidades_de_tempo_por_periodo': Periodo.UnidadeDeTempo.DIA,
            'numero_de_periodos': 10,
            'promocao_submit': 'Salvar',
        }

        response = self.client.post(self._get_url(scope.pk), data=data)

        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(
            list(response.context['promocao'].produtos.all()),
            list(promocao.produtos.all()),
        )
