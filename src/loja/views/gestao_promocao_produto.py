from typing import Any

from django.db.models import F, ExpressionWrapper, DecimalField
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from loja.models.funcionario import GerenteFinanceiro
from util.views import UpdateHTMXView, QueryView
from loja.models import Produto, Promocao
from loja.views import LojaProtectionMixin
from loja.forms import *
from util.mixins import MultipleFormsViewMixin


class GestaoPromocoesProdutoCRUDView(
    MultipleFormsViewMixin,
    QueryView,
    LojaProtectionMixin,
    LoginRequiredMixin,
    UpdateHTMXView,
    DetailView,
):
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True
    template_name = 'gestao_oferta_produtos/promocoes_por_produto.html'
    model = Produto
    usuario_class = GerenteFinanceiro
    query_forms_class = {
        'promocao': PromocaoQueryForm,
        'produto': ProdutoQueryForm,
    }
    query_form_class = PromocaoQueryForm
    forms_class = {
        'promocoes_por_produto': PromocoesPorProdutoForm,
        'preco_de_venda': PrecoDeVendaProdutoForm,
        'em_venda': ProdutoEmVendaForm,
        'duplicar_promocao': DuplicarPromocaoForm,
    }

    def get_template_names(self, request=None) -> list[str]:
        templates = [self.template_name]

        request = self.request
        cards = request.GET.get('visualizacao') == 'cards'

        if 'promocoes' in request.POST:
            templates.append(
                'gestao_oferta_produtos/listas/lista_promocoes_produto.html'
            )
        elif self.query_forms_class['promocao'].submit_name() in request.POST:
            templates.append(
                'gestao_oferta_produtos/listas/lista_choices_promocoes_produto.html'
            )
        elif self.query_forms_class['produto'].submit_name() in request.POST:
            templates.append(
                'gestao_oferta_produtos/listas/lista_choices_produtos_promocao.html'
            )
        elif 'data_inicio' in request.POST:
            if cards:
                templates.append(
                    'gestao_oferta_produtos/cards/card_promocao_produto.html'
                )
            else:
                templates.append(
                    'gestao_oferta_produtos/linhas/linha_promocao_produto.html'
                )
        elif 'em_venda' in request.POST or 'preco_de_venda' in request.POST:
            templates.append(
                'gestao_oferta_produtos/articles/article_produto_oferta.html'
            )

        return templates

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = {}
        kwargs['loja'] = self.get_loja()

        if form_class is None and request is not None:
            form_class = self.get_form_class(request)

        if request is not None:
            kwargs['data'] = request.POST

        if form_class != self.forms_class['duplicar_promocao']:
            kwargs['instance'] = self.get_object()

        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        produto = self.get_object()

        forms = self.get_forms()
        for key, form in forms.items():
            context[form.form_name()] = form

        for form in self.query_forms_class.values():
            context[form.form_name()] = form()

        context['produto'] = produto
        context['promocoes'] = produto.promocoes.all().with_desconto(
            produto.preco_de_venda
        )

        return context

    def form_valid(self, form):
        object = form.save()
        context = {}
        context['erros'] = form.errors

        if type(form) == self.forms_class['preco_de_venda']:
            return JsonResponse(
                {'success': True, 'preco_de_venda': object.preco_de_venda}
            )
        elif type(object) is Promocao:
            self.object = Produto.produtos.get(pk=self.kwargs['pk'])
            context['promocao'] = (
                Promocao.promocoes.filter(pk=object.pk)
                .with_desconto(self.object.preco_de_venda)
                .first()
            )
        else:
            self.object = object
            context['produto'] = self.object
            context['promocoes'] = self.object.promocoes.all()

        context['success'] = True

        return render(self.request, self.get_template_names()[1], context)

    def pesquisar_promocoes(self, request: HttpRequest) -> HttpResponse:
        queryset = self.search(
            request,
            query_form_class=self.query_forms_class['promocao'],
            queryset=Promocao.promocoes.filter(loja=self.get_loja()),
        )
        queryset = queryset.with_desconto(self.get_object().preco_de_venda)

        return render(
            request,
            self.get_template_names()[1],
            {
                'promocoes_choices': queryset,
            },
        )

    def pesquisar_produtos(self, request: HttpRequest) -> HttpResponse:
        queryset = self.search(
            request,
            query_form_class=self.query_forms_class['produto'],
            queryset=Produto.produtos.filter(loja=self.get_loja()),
        )
        # queryset = queryset.with_desconto(self.get_object().preco_de_venda)

        return render(
            request,
            self.get_template_names()[1],
            {'produtos_choices': queryset},
        )

    def post(self, request, *args, **kwargs):
        try:
            if self.query_forms_class['promocao'].submit_name() in request.POST:
                return self.pesquisar_promocoes(request)
            elif self.query_forms_class['produto'].submit_name() in request.POST:
                return self.pesquisar_produtos(request)
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'type': 'error', 'message': str(e)}, status=400
            )


class GestaoProdutosPromocaoCRUDView(
    MultipleFormsViewMixin,
    QueryView,
    LojaProtectionMixin,
    LoginRequiredMixin,
    UpdateHTMXView,
    DetailView,
):
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True
    template_name = 'gestao_oferta_produtos/produtos_por_promocao.html'
    model = Promocao
    usuario_class = GerenteFinanceiro
    query_form_class = ProdutoQueryForm
    forms_class = {
        'produtos_por_promocao': ProdutosPorPromocaoForm,
        'duplicar_promocao': DuplicarPromocaoForm,
    }

    def get_template_names(self, request=None) -> list[str]:
        templates = [self.template_name]

        request = self.request

        if 'produtos' in request.POST:
            templates.append(
                'gestao_oferta_produtos/listas/lista_produtos_promocao.html'
            )
        elif 'data_inicio' in request.POST:
            templates.append('gestao_oferta_produtos/articles/article_promocao.html')
        elif self.query_form_class.submit_name() in request.POST:
            templates.append(
                'gestao_oferta_produtos/listas/lista_choices_produtos_promocao.html'
            )

        return templates

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        context[self.query_form_class.form_name()] = self.query_form_class()
        promocao = self.get_object()
        context['promocao'] = promocao
        context['produtos'] = promocao.produtos.all().with_desconto(
            promocao.porcentagem_desconto
        )
        context['data_final'] = promocao.data_inicio + promocao.periodo.tempo_total
        context['today'] = date.today()

        return context

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['loja'] = self.get_loja()
        # kwargs['scope'] = self.scope
        kwargs['instance'] = self.get_object()

        if request is not None:
            kwargs['data'] = request.POST

        # kwargs['loja'] = self.get_loja()

        return kwargs

    def form_valid(self, form):
        object = form.save()
        context = {}
        context['erros'] = form.errors

        if type(form) == self.forms_class['produtos_por_promocao']:
            self.object = object
            context['promocao'] = object
            context['produtos'] = object.produtos.all().with_desconto(
                object.porcentagem_desconto
            )

            return render(self.request, self.get_template_names()[1], context)
        elif type(form) == self.forms_class['duplicar_promocao']:
            return redirect(
                reverse(
                    'gerir_produtos_promocao',
                    kwargs={'loja_scope': self.scope.pk, 'pk': object.pk},
                )
            )

    def pesquisar_produtos(self, request: HttpRequest) -> HttpResponse:
        queryset = self.search(
            request, queryset=Produto.produtos.filter(loja=self.get_loja())
        )
        queryset = queryset.with_desconto(self.get_object().porcentagem_desconto)

        return render(
            request,
            self.get_template_names()[1],
            {'produtos_choices': queryset},
        )

    def post(self, request, *args, **kwargs):
        try:
            if self.query_form_class.submit_name() in request.POST:
                return self.pesquisar_produtos(request)
            return super().post(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse(
                {'success': False, 'type': 'error', 'message': str(e)}, status=400
            )
