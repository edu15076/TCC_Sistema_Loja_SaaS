from typing import Any

from django.db.models.query import QuerySet
from django.http.response import HttpResponseRedirect
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from loja.models.funcionario import GerenteFinanceiro
from util.views.htmx import UpdateHTMXView
from common.views.mixins import UsuarioMixin
from loja.models import Produto, Promocao
from loja.views import UserFromLojaRequiredMixin
from common.models import Periodo
from loja.forms import (
    PrecoDeVendaProdutoForm,
    ProdutoEmVendaForm,
    PromocoesPorProdutoForm,
    DuplicarPromocaoForm,
)


class GestaoPromocoesProdutoCRUDView(UserFromLojaRequiredMixin, UpdateHTMXView, DetailView):
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

        if 'promocoes' in request.POST or 'data_inicio' in request.POST:
            templates.append('includes/lista_promocoes_produto.html')
        elif 'em_venda' in request.POST or 'preco_de_venda' in request.POST:
            if cards:
                templates.append('cards/card_oferta_produto.html')
            else:
                templates.append('linhas/linha_oferta_produto.html')

        return templates

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = {}
        produto = self.get_object()

        context['produto'] = produto
        context['form'] = self.promocoes_form_class(scope=self.scope, instance=produto)
        context['preco_form'] = self.preco_form_class(instance=produto)
        context['em_venda_form'] = self.em_venda_form_class(instance=produto)

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
