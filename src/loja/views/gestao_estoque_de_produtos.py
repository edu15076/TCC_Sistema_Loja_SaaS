from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.views.mixins import UserFromLojaRequiredMixin
from loja.models import Funcionario, ProdutoPorLote, GerenteDeEstoque

__all__ = (
    'GestaoEstoqueDeProdutosListView',
)

class GestaoEstoqueDeProdutosListView(
    UserFromLojaRequiredMixin, CreateOrUpdateListHTMXView
):
    # TODO: Validar permissões e bloquear edição de produtos que não são da mesma loja usando o Mixin mais apropriado
    template_name = 'estoque_de_produtos.html'
    usuario_class = GerenteDeEstoque
    model = ProdutoPorLote

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page().filter(produto__loja=self.user.loja)
        return render(request, self.template_name, {'estoque': queryset})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        acao = request.POST.get('acao')
        produto_id = request.POST.get('id')

        produto = self.model.produtos_por_lote.get(id=produto_id)

        if acao == "atualizar":
            qtd_em_estoque = request.POST.get('qtd_em_estoque')
            produto.qtd_em_estoque = qtd_em_estoque
            produto.save()
        elif acao == "deletar":
            produto.delete()

        return render(request, self.template_name, {'estoque': self.get_page().filter(produto__loja=self.user.loja)})
