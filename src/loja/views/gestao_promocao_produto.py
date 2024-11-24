from typing import Any

from django.db.models.query import QuerySet
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from common.models.scopes import LojaScope
from util.views.edit_list import CreateOrUpdateListHTMXView
from util.views.htmx import UpdateHTMXView
from common.views.mixins import UsuarioMixin
from loja.models import Produto, Promocao
from common.models import Periodo
from loja.forms import (
    PrecoDeVendaProdutoForm,
    ProdutoEmVendaForm,
    PromocoesPorProdutoForm,
    DuplicarPromocaoForm,
)


class GestaoPromocoesProdutoCRUDView(UpdateHTMXView, DetailView):
    # TODO adcionar scopo e validação de permissão
    model = Produto
    promocoes_form_class = PromocoesPorProdutoForm
    preco_form_class = PrecoDeVendaProdutoForm
    em_venda_form_class = ProdutoEmVendaForm
    duplicar_promocao_form_class = DuplicarPromocaoForm
    template_name = 'promocoes_por_produto.html'

    def get_template_produto(self, request: HttpRequest) -> str:
        return 'includes/linha_tabela_oferta_produto.html'

        visualizacao = request.GET.get('visualizacao')
        if visualizacao == 'tabela' or visualizacao is None:
            return 'includes/linha_tabela_oferta_produto.html'
        else:
            return 'cards/card_oferta_produto.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # context = super().get_context_data(**kwargs)
        context = {}
        produto = self.get_object()

        context['produto'] = produto
        context['form'] = self.promocoes_form_class(instance=produto)
        context['promocoes_form'] = self.promocoes_form_class(instance=produto)
        context['preco_form'] = self.preco_form_class(instance=produto)
        context['em_venda_form'] = self.em_venda_form_class(instance=produto)
        context['scope'] = 1

        return context

    def form_valid(self, form):
        return_value = form.save()
        context = {}
        template = self.get_template_produto(self.request)

        if type(return_value) == tuple:
            object, errors = return_value
            context['erros'] = errors

            if type(object) is Produto:
                self.object = object
                context['promocoes'] = self.object.promocoes.all()
                # template = 'includes/lista_promocoes_produto.html'
            else:
                self.object = Produto.produtos.get(pk=self.kwargs['pk'])
                context['promocao'] = object
                # template = 'includes/item_lista_promocoes_produto.html'
        else:
            self.object = return_value

        context['produto'] = self.object
        context['success'] = True

        return render(self.request, template, context)

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        try:
            produto = self.get_object()

            if 'promocoes' in request.POST:
                form = self.promocoes_form_class(data=request.POST, instance=produto)
            elif 'data_inicio' in request.POST:
                form = self.duplicar_promocao_form_class(
                    data=request.POST, loja=produto.loja
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
