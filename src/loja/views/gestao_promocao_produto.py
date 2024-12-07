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
from util.mixins import MultipleFormsViewMixin


class GestaoPromocoesProdutoCRUDView(
    MultipleFormsViewMixin,
    UserFromLojaRequiredMixin,
    FilterForSameLojaMixin,
    UpdateHTMXView,
    DetailView,
):
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True
    template_name = 'promocoes_por_produto.html'
    model = Produto
    usuario_class = GerenteFinanceiro
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
            templates.append('includes/lista_promocoes_produto.html')
        elif 'data_inicio' in request.POST:
            if cards:
                templates.append('cards/card_promocao_produto.html')
            else:
                templates.append('linhas/linha_promocao_produto.html')
        elif 'em_venda' in request.POST or 'preco_de_venda' in request.POST:
            templates.append('includes/article_produto_oferta.html')

        return templates

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = {}

        if form_class is None and request is not None:
            form_class = self.get_form_class(request)

        if request is not None:
            kwargs['data'] = request.POST

        if (
            form_class != self.forms_class['em_venda']
            and form_class != self.forms_class['preco_de_venda']
        ):
            kwargs['scope'] = self.scope

        if form_class != self.forms_class['duplicar_promocao']:
            kwargs['instance'] = self.get_object()

        return kwargs

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        produto = self.get_object()

        forms = self.get_forms()
        for key, form in forms.items():
            context[f"{key}_form"] = form

        context['produto'] = produto
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
            context['promocao'] = (
                Promocao.promocoes.filter(pk=object.pk)
                .annotate(
                    desconto=ExpressionWrapper(
                        self.object.preco_de_venda * F('porcentagem_desconto') / 100,
                        output_field=DecimalField(),
                    ),
                    preco_com_desconto=ExpressionWrapper(
                        self.object.preco_de_venda - F('desconto'),
                        output_field=DecimalField(),
                    ),
                )
                .first()
            )
        else:
            self.object = object
            context['produto'] = self.object
            context['promocoes'] = self.object.promocoes.all()

        context['success'] = True

        return render(self.request, self.get_template_names()[1], context)


class GestaoProdutosPromocaoCRUDView(
    MultipleFormsViewMixin,
    UserFromLojaRequiredMixin,
    FilterForSameLojaMixin,
    UpdateHTMXView,
    DetailView,
):
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True
    template_name = 'produtos_por_promocao.html'
    model = Promocao
    usuario_class = GerenteFinanceiro
    forms_class = {
        'produtos_por_promocao': ProdutosPorPromocaoForm,
        'duplicar_promocao': DuplicarPromocaoForm,
    }

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

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        promocao = self.get_object()
        context['promocao'] = promocao
        context['produtos'] = promocao.produtos.all().annotate(
            desconto=ExpressionWrapper(
                F('preco_de_venda') * (promocao.porcentagem_desconto / 100),
                output_field=DecimalField(),
            ),
            preco_com_desconto=F('preco_de_venda') - F('desconto'),
        )
        context['data_final'] = promocao.data_inicio + promocao.periodo.tempo_total
        context['today'] = date.today()

        return context

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.scope
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
            context['produtos'] = object.produtos.all().annotate(
                desconto=ExpressionWrapper(
                    F('preco_de_venda') * (object.porcentagem_desconto / 100),
                    output_field=DecimalField(),
                ),
                preco_com_desconto=F('preco_de_venda') - F('desconto'),
            )

            return render(self.request, self.get_template_names()[1], context)
        elif type(form) == self.forms_class['duplicar_promocao']:
            return redirect(
                reverse(
                    'gestao_produtos_promocao',
                    kwargs={'loja_scope': self.scope.pk, 'pk': object.pk},
                )
            )
