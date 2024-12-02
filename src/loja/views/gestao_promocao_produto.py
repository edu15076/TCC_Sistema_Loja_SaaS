from typing import Any

from django.db.models import F, ExpressionWrapper, DecimalField
from django.forms.forms import BaseForm
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import redirect, render

from loja.models.funcionario import GerenteFinanceiro
from util.views.htmx import UpdateHTMXView
from loja.models import Produto, Promocao
from loja.views import UserFromLojaRequiredMixin, FilterForSameLojaMixin
from loja.forms import *


class GestaoPromocoesProdutoCRUDView(
    UserFromLojaRequiredMixin, FilterForSameLojaMixin, UpdateHTMXView, DetailView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'promocoes_por_produto.html'
    model = Produto
    promocoes_form_class = PromocoesPorProdutoForm
    preco_form_class = PrecoDeVendaProdutoForm
    em_venda_form_class = ProdutoEmVendaForm
    duplicar_promocao_form_class = DuplicarPromocaoForm
    usuario_class = GerenteFinanceiro
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True

    def get_template_names(self, request=None) -> list[str]:
        templates = [self.template_name]

        request = self.request
        cards = request.GET.get('visualizacao') == 'cards'

        if 'promocoes' in request.POST:
            templates.append('includes/lista_promocoes_produto.html')
        elif 'data_inicio' in request.POST:
            if cards:
                templates.append('cards/card_promocao_produto.html')
            else:
                templates.append('linhas/linha_promocao_produto.html')
        elif 'em_venda' in request.POST or 'preco_de_venda' in request.POST:
            templates.append('includes/article_produto_oferta.html')

        return templates
    
    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.scope
        kwargs['instance'] = self.get_object()
        # kwargs['loja'] = self.get_loja()

        return kwargs
    
    def get_form(self, form_class: type | None = ...) -> BaseForm:
        kwargs = self.get_form_kwargs()

        if form_class != self.promocoes_form_class:
            kwargs.pop('scope')

        return form_class(**kwargs)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        produto = self.get_object()

        context['produto'] = produto
        context['form'] = self.get_form(self.promocoes_form_class)
        context['preco_form'] = self.get_form(self.preco_form_class)
        context['em_venda_form'] = self.get_form(self.em_venda_form_class)
        context['promocoes'] = produto.promocoes.all().annotate(
            desconto=ExpressionWrapper(
                produto.preco_de_venda * F('porcentagem_desconto') / 100,
                output_field=DecimalField(),
            ),
            preco_com_desconto=ExpressionWrapper(
                produto.preco_de_venda - F('desconto'),
                output_field=DecimalField(),
            ),
        )

        return context

    def form_valid(self, form):
        object = form.save()
        context = {}
        context['erros'] = form.errors

        if type(object) is Promocao:
            self.object = Produto.produtos.get(pk=self.kwargs['pk'])
            context['promocao'] = object
        else:
            self.object = object
            context['produto'] = self.object
            context['promocoes'] = self.object.promocoes.all()

        context['success'] = True

        return render(self.request, self.get_template_names()[1], context)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            produto = self.get_object()

            if 'promocoes' in request.POST:
                form = self.promocoes_form_class(
                    data=request.POST, scope=self.scope, instance=produto
                )
            elif 'data_inicio' in request.POST:
                form = self.duplicar_promocao_form_class(
                    data=request.POST, scope=self.scope
                )
            elif 'preco_de_venda' in request.POST:
                form = self.preco_form_class(request.POST, instance=produto)
            elif 'em_venda' in request.POST:
                form = self.em_venda_form_class(request.POST, instance=produto)

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)


class GestaoProdutosPromocaoCRUDView(
    UserFromLojaRequiredMixin, FilterForSameLojaMixin, UpdateHTMXView, DetailView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'produtos_por_promocao.html'
    model = Promocao
    produtos_form_class = ProdutosPorPromocaoForm
    duplicar_promocao_form_class = DuplicarPromocaoForm
    usuario_class = GerenteFinanceiro
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True

    def get_template_names(self, request=None) -> list[str]:
        templates = [self.template_name]

        request = self.request

        if 'produtos' in request.POST:
            templates.append('includes/lista_produtos_promocao.html')
        elif 'data_inicio' in request.POST:
            templates.append('includes/article_promocao.html')

        return templates

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}

        promocao = self.get_object()
        context['promocao'] = promocao
        context['produtos'] = promocao.produtos.all().annotate(
            desconto=ExpressionWrapper(
                F('preco_de_venda') * (promocao.porcentagem_desconto / 100),
                output_field=DecimalField(),
            ),
            preco_com_desconto=F('preco_de_venda') - F('desconto'),
        )
        context['form'] = self.get_form(self.produtos_form_class)
        context['duplicar_form'] = self.get_form(self.duplicar_promocao_form_class)
        context['data_final'] = promocao.data_inicio + promocao.periodo.tempo_total
        context['today'] = date.today()

        return context

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.scope
        kwargs['instance'] = self.get_object()
        # kwargs['loja'] = self.get_loja()

        return kwargs

    def form_valid(self, form):
        object = form.save()
        context = {}
        context['erros'] = form.errors

        if type(form) == self.produtos_form_class:
            self.object = object
            context['promocao'] = object
            context['produtos'] = object.produtos.all().annotate(
                desconto=ExpressionWrapper(
                    F('preco_de_venda') * (object.porcentagem_desconto / 100),
                    output_field=DecimalField(),
                ),
                preco_com_desconto=F('preco_de_venda') - F('desconto'),
            )

            return render(self.request, self.get_template_names()[1], context)
        elif type(form) == self.duplicar_promocao_form_class:
            return redirect(
                reverse(
                    'gestao_produtos_promocao',
                    kwargs={'loja_scope': self.scope.pk, 'pk': object.pk},
                )
            )

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            promocao = self.get_object()
            form = None

            if 'data_inicio' in request.POST:
                form = self.duplicar_promocao_form_class(
                    data=request.POST, scope=self.scope, instance=promocao
                )
            elif 'produtos' in request.POST:
                form = self.produtos_form_class(
                    data=request.POST, scope=self.scope, instance=promocao
                )

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
