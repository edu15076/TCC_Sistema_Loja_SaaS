from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.views.mixins import UserFromLojaRequiredMixin
from loja.models import Funcionario, ProdutoPorLote

__all__ = (
    'GestaoEstoqueDeProdutosListView',
)


class GestaoEstoqueDeProdutosListView(
    UserFromLojaRequiredMixin, CreateOrUpdateListHTMXView
):
    template_name = 'estoque_de_produtos.html'
    usuario_class = Funcionario
    model = ProdutoPorLote

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page()

        return render(request, self.template_name, {'estoque': queryset})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return JsonResponse({'success': True}, status=200)