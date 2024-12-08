from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from util.mixins import MultipleFormsViewMixin
from loja.views.mixins import LojaProtectionMixin
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Produto, GerenteFinanceiro, ConfiguracaoDeVendas
from loja.forms import (
    ConfiguracaoDeVendasForm,
    PrecoDeVendaProdutoForm,
    ProdutoEmVendaForm,
    OfertaProdutosFilterForm,
    ProdutoQueryForm,
)


class GestaoOfertaProdutoListView(
    MultipleFormsViewMixin,
    LojaProtectionMixin,
    LoginRequiredMixin,
    CreateOrUpdateListHTMXView,
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'gestao_oferta_produtos/oferta_produtos.html'
    permission_required = 'loja.gerir_oferta_de_produto'
    usuario_class = GerenteFinanceiro
    raise_exception = True
    filter_form = OfertaProdutosFilterForm
    query_form = ProdutoQueryForm
    model = Produto
    object_pk = None
    object = None
    default_order = ['id']
    paginate_by = 30
    forms_class = {
        'preco_de_venda': PrecoDeVendaProdutoForm,
        'em_venda': ProdutoEmVendaForm,
        'configuracao_de_venda': ConfiguracaoDeVendasForm,
    }

    def get_pk_slug(self) -> tuple[int | None, str | None]:
        return self.object_pk, None

    def get_object(self, queryset: QuerySet[Any] | None = None):
        object = super().get_object(queryset)

        if object is None:
            raise Exception('Produto não encontrado.')

        return object

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(loja__scope=self.scope)

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, Any]:
        kwargs = {}
        kwargs['loja'] = self.get_loja()

        if request is not None:
            if self.forms_class['configuracao_de_venda'].submit_name() in request.POST:
                # kwargs['scope'] = self.scope
                pass
            else:
                kwargs['instance'] = self.get_object()

            kwargs['data'] = request.POST

        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object_list = self.get_queryset()
        context = super().get_context_data()

        form = self.get_forms()
        for form in form.values():
            context[form.form_name()] = form

        context['configuracao_de_venda'] = ConfiguracaoDeVendas.configuracoes.get(
            loja__scope=self.scope
        )
        context['filter_form'] = self.filter_form()
        context['query_form'] = self.query_form()
        context['produtos'] = self.get_page()
        context['produtos_count'] = Produto.produtos.filter(
            loja__scope=self.scope
        ).count()

        return context

    def get_template_names(self) -> list[str]:
        if self.request is None:
            return [self.template_name]

        request = self.request
        cards = request.GET.get('visualizacao') == 'cards'

        if 'em_venda_submit' in request.POST or 'preco_de_venda_submit' in request.POST:
            if cards:
                return ['gestao_oferta_produtos//cards/card_oferta_produto.html']
            else:
                return ['gestao_oferta_produtos/linhas/linha_oferta_produto.html']
        elif 'query' in request.POST:
            return ['gestao_oferta_produtos/listas/lista_ofertas_produtos.html']

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def pesquisar_produtos(self, request: HttpRequest) -> HttpResponse:
        query_form = self.query_form(request.POST)
        queryset = self.get_queryset()

        if query_form.is_valid():
            query_parameters = query_form.get_parameters()
            queryset = queryset.filter(**query_parameters)

        return render(
            request,
            self.get_template_names()[0],
            {
                'produtos': queryset,
                'em_venda_form': self.get_form(self.forms_class['em_venda']),
                'preco_form': self.get_form(self.forms_class['preco_de_venda']),
            },
        )

    def form_valid(self, form):
        if type(form) == self.forms_class['configuracao_de_venda']:
            configuracao = form.save()
            return JsonResponse(
                {
                    'success': True,
                    'limite_porcentagem_desconto_maximo': configuracao.limite_porcentagem_desconto_maximo,
                }
            )

        produto = form.save()
        return render(
            self.request,
            self.get_template_names()[0],
            {
                'produto': produto,
                self.forms_class['em_venda'].form_name(): self.get_form(
                    self.forms_class['em_venda']
                ),
                self.forms_class['preco_de_venda'].form_name(): self.get_form(
                    self.forms_class['preco_de_venda']
                ),
                'success': True,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            if 'query' in request.POST:
                return self.pesquisar_produtos(request)
            else:
                self.object_pk = request.POST.get('id')
                return super().post(request)

        except Exception as e:
            return JsonResponse(
                {'success': False, 'type': 'error', 'message': str(e)}, status=400
            )
