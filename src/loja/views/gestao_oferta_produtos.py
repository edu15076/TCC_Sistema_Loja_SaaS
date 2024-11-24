from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from common.models.scopes import LojaScope
from util.views.edit_list import CreateOrUpdateListHTMXView
from common.views.mixins import UsuarioMixin
from loja.models import Produto, Promocao
from common.models import Periodo
from loja.forms import (
    PrecoDeVendaProdutoForm,
    ProdutoEmVendaForm,
    OfertaProdutosFilterForm,
    ProdutoQueryForm,
)


class GestaoOfertaProdutoListView(
    # LoginRequiredMixin, UsuarioMixin, CreateOrUpdateListHTMXView
    CreateOrUpdateListHTMXView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'oferta_produtos.html'
    preco_form_class = PrecoDeVendaProdutoForm
    em_venda_form_class = ProdutoEmVendaForm
    filter_form = OfertaProdutosFilterForm
    query_form = ProdutoQueryForm
    model = Produto
    object_pk = None
    object = None
    default_order = ['id']
    paginate_by = 30

    def get_pk_slug(self) -> tuple[int | None, str | None]:
        return self.object_pk, None

    def get_object(self, queryset: QuerySet[Any] | None = None):
        object = super().get_object(queryset)

        if object is None:
            raise Exception('Produto não encontrado.')

        return object

    # def get_queryset(self) -> QuerySet[Any]:
    #     # queryset = super().get_queryset().filter(loja=self.user.loja)
    #     query_parameter = self.query_form(self.request.POST)
    #     print(query_parameter.is_valid())
    #     print(query_parameter.errors)
    #     print(query_parameter.cleaned_data)
    #     # if query_parameter:
    #     #     queryset = queryset.filter(**query_parameter)

    # return queryset

    def get_form(self, form_class: type | None = ...):
        return None

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object_list = self.get_queryset()
        context = super().get_context_data()
        # context = {}
        context['preco_form'] = self.preco_form_class()
        context['em_venda_form'] = self.em_venda_form_class()
        context['filter_form'] = self.filter_form()
        context['query_form'] = self.query_form()
        context['produtos'] = self.get_page()
        context['produtos_count'] = self.model.produtos.count()

        # todo remover
        context['scope'] = 1

        return context

    def get_template_produto(self, request: HttpRequest) -> str:
        return 'includes/linha_tabela_oferta_produto.html'

        visualizacao = request.GET.get('visualizacao')
        if visualizacao == 'tabela' or visualizacao is None:
            return 'includes/linha_tabela_oferta_produto.html'
        else:
            return 'cards/card_oferta_produto.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def pesquisar_produtos(self, request: HttpRequest) -> HttpResponse:
        query_form = self.query_form(request.POST)
        queryset = self.get_queryset()

        if query_form.is_valid():
            query_parameters = query_form.get_parameters()

            queryset = queryset.filter(**query_parameters)

        return render(
            request, 'includes/exibe_ofertas_produtos.html', {'produtos': queryset}
        )

    def form_valid(self, form):
        produto = form.save()
        return render(
            self.request,
            self.get_template_produto(self.request),
            {'produto': produto, 'success': True},
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            if 'query' in request.POST:
                return self.pesquisar_produtos(request)
            if 'preco_de_venda' in request.POST:
                self.object_pk = request.POST.get('pk')
                form = self.preco_form_class(request.POST, instance=self.get_object())
            elif 'em_venda' in request.POST:
                self.object_pk = request.POST.get('pk')
                form = self.em_venda_form_class(
                    request.POST, instance=self.get_object()
                )

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
