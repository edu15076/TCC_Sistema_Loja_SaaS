from typing import Any

from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from django.shortcuts import render

from util.mixins import MultipleFormsViewMixin
from loja.models.funcionario import GerenteFinanceiro
from loja.views.mixins import UserFromLojaRequiredMixin
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Produto
from loja.forms import (
    PrecoDeVendaProdutoForm,
    ProdutoEmVendaForm,
    OfertaProdutosFilterForm,
    ProdutoQueryForm,
)

# TODO - Refatorar para usar get_form_kwargs


class GestaoOfertaProdutoListView(
    MultipleFormsViewMixin, UserFromLojaRequiredMixin, CreateOrUpdateListHTMXView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'oferta_produtos.html'
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
        # kwargs['scope'] = self.scope
        if request is not None:
            kwargs['instance'] = self.get_object()
            kwargs['data'] = request.POST

        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        self.object_list = self.get_queryset()
        context = super().get_context_data()

        form = self.get_forms()
        for form in form.values():
            context[form.form_name()] = form

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
                return ['cards/card_oferta_produto.html']
            else:
                return ['linhas/linha_oferta_produto.html']
        elif 'query' in request.POST:
            return ['includes/exibe_ofertas_produtos.html']

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
        produto = form.save()
        return render(
            self.request,
            self.get_template_names()[0],
            {
                'produto': produto,
                self.forms_class['em_venda'].form_name(): self.get_form(self.forms_class['em_venda']),
                self.forms_class['preco_de_venda'].form_name(): self.get_form(self.forms_class['preco_de_venda']),
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
            return JsonResponse({'success': False, 'type':'error', 'message': str(e)}, status=400)
