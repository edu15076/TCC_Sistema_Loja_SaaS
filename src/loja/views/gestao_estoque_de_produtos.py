from typing import Any

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView, DeleteView

from loja.forms import ProdutoCreationForm, ProdutoEditForm, ProdutoPorLoteDeleteForm, \
    ProdutoPorLoteCreationForm, ProdutoPorLoteEditForm
from util.views import CreateHTMXView, HTMXHelperMixin, UpdateHTMXView, DeleteHTMXView
from loja.views.mixins import UserFromLojaRequiredMixin, LojaProtectionMixin
from loja.models import ProdutoPorLote, GerenteDeEstoque, Produto

__all__ = (
    'CriarProdutoView',
    'UpdateProdutoView',
    'ListProdutosView',
    'CardProdutoView',
    'CardProdutoEditView',
    'CriarProdutoPorLoteView',
    'UpdateProdutoPorLoteView',
    'ListProdutosPorLoteView',
    'CardProdutoPorLoteView',
    'DeleteProdutoPorLoteView',
    'GestaoProdutosPorLoteView',
    'GestaoProdutosEstoqueView',
)


class CriarProdutoView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, CreateHTMXView
):
    template_name = 'gestao_estoque/modals/modal_criar_produto.html'
    form_template_name = 'gestao_estoque/forms/htmx_create_produto.html'
    model = Produto
    form_class = ProdutoCreationForm
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_produtos_cadastrados'

    def get_form_action(self):
        return reverse('criar_produto_estoque', kwargs={'loja_scope': int(self.scope)})

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja
        }

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse(
            'produto_estoque_detail_edit',
            kwargs={'pk': self.object.pk, 'loja_scope': int(self.scope)}
        )


class UpdateProdutoView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, UpdateHTMXView
):
    template_name = 'gestao_estoque/modals/modal_editar_produto.html'
    form_template_name = 'gestao_estoque/forms/htmx_edit_produto.html'
    model = Produto
    form_class = ProdutoEditForm
    context_object_name = 'produto'
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_produtos_cadastrados'

    def get_form_action(self):
        return reverse('editar_produto_estoque', kwargs={
            'loja_scope': int(self.scope),
            'pk': self.object.pk
        })

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'instance': self.object,
            'auto_id': f'editar-produto-{self.object.pk}-%s'
        }

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse(
            'produto_estoque_detail',
            kwargs={'pk': self.object.pk, 'loja_scope': int(self.scope)}
        )


class ProdutoContextDataMixin:
    def get_edit_form(self, produto: Produto):
        return ProdutoEditForm(
            loja=self.user.loja,
            instance=produto,
            auto_id=f'editar-produto-{produto.pk}-%s'
        )

    def get_context_data_produto(self, produto: Produto) -> Produto:
        produto.edit_form = self.get_edit_form(produto)
        return produto


class ListProdutosView(
    LojaProtectionMixin,
    PermissionRequiredMixin,
    ProdutoContextDataMixin,
    HTMXHelperMixin,
    ListView  # TODO: Trocar para FilterListView e usar busca de produtos
):
    template_name = 'gestao_estoque/includes/list_produtos.html'
    restrict_direct_access = True
    model = Produto
    context_object_name = 'produtos'
    ordering = ['-em_venda', 'descricao']

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_produtos_cadastrados'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for produto in context['produtos']:
            self.get_context_data_produto(produto)
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CardProdutoView(
    LojaProtectionMixin,
    PermissionRequiredMixin,
    ProdutoContextDataMixin,
    HTMXHelperMixin,
    DetailView
):
    template_name = 'gestao_estoque/cards/card_produto.html'
    restrict_direct_access = True
    model = Produto
    context_object_name = 'produto'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_produtos_cadastrados'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_context_data_produto(context['produto'])
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CardProdutoEditView(CardProdutoView):
    template_name = 'gestao_estoque/cards/card_produto_edit.html'


class GestaoProdutosEstoqueView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, TemplateView
):
    template_name = 'gestao_estoque/gestao_produtos.html'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_produtos_cadastrados'

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CriarProdutoPorLoteView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, CreateHTMXView
):
    template_name = 'gestao_produto/modals/modal_criar_produto_por_lote.html'
    form_template_name = 'gestao_produto/forms/htmx_create_produto_por_lote.html'
    model = ProdutoPorLote
    form_class = ProdutoPorLoteCreationForm
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get_form_action(self):
        return reverse('criar_produto_por_lote', kwargs={
            'loja_scope': int(self.scope),
            'produto_pk': self.kwargs.get('produto_pk')
        })

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'produto': Produto.produtos.get(pk=self.kwargs.get('produto_pk'))
        }

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse(
            'produto_por_lote_detail',
            kwargs={
                'pk': self.object.pk,
                'loja_scope': int(self.scope),
                'produto_pk': self.kwargs.get('produto_pk')
            }
        )


class UpdateProdutoPorLoteView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, UpdateHTMXView
):
    template_name = 'gestao_produto/modals/modal_editar_produto_por_lote.html'
    form_template_name = 'gestao_produto/forms/htmx_edit_produto_por_lote.html'
    model = ProdutoPorLote
    form_class = ProdutoPorLoteEditForm
    context_object_name = 'lote'
    success_url = None
    redirect_on_success = False
    restrict_direct_access = False
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'
    form_error_status_code = 299

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get_form_action(self):
        return reverse('editar_produto_por_lote', kwargs={
            'loja_scope': int(self.scope),
            'produto_pk': self.kwargs.get('produto_pk'),
            'pk': self.object.pk
        })

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'instance': self.object,
            'produto': Produto.produtos.get(pk=self.kwargs.get('produto_pk')),
            'auto_id': f'editar-produto-por-lote-{self.object.pk}-%s'
        }

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})

    def get_success_url(self):
        return reverse(
            'produto_por_lote_detail',
            kwargs={
                'pk': self.object.pk,
                'loja_scope': int(self.scope),
                'produto_pk': self.kwargs.get('produto_pk')
            }
        )


class ProdutoPorLoteContextDataMixin:
    def get_edit_form(self, produto_por_lote: ProdutoPorLote):
        return ProdutoPorLoteEditForm(
            loja=self.user.loja,
            instance=produto_por_lote,
            produto=produto_por_lote.produto,
            auto_id=f'editar-produto-por-lote-{produto_por_lote.pk}-%s'
        )

    def get_delete_form(self, produto_por_lote: ProdutoPorLote):
        return ProdutoPorLoteDeleteForm(
            loja=self.user.loja,
            lote=produto_por_lote,
            produto=produto_por_lote.produto,
            auto_id=f'delete-produto-por-lote-{produto_por_lote.pk}-%s'
        )

    def get_context_data_produto(
            self, produto_por_lote: ProdutoPorLote
    ) -> ProdutoPorLote:
        produto_por_lote.edit_form = self.get_edit_form(produto_por_lote)
        produto_por_lote.delete_form = self.get_delete_form(produto_por_lote)
        return produto_por_lote


class ListProdutosPorLoteView(
    LojaProtectionMixin,
    PermissionRequiredMixin,
    ProdutoPorLoteContextDataMixin,
    HTMXHelperMixin,
    ListView
):
    template_name = 'gestao_produto/includes/table_produto_por_lote.html'
    restrict_direct_access = False
    model = ProdutoPorLote
    context_object_name = 'lotes'
    ordering = ['-qtd_em_estoque', 'lote']

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for lote in context['lotes']:
            self.get_context_data_produto(lote)
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CardProdutoPorLoteView(
    LojaProtectionMixin,
    PermissionRequiredMixin,
    ProdutoPorLoteContextDataMixin,
    HTMXHelperMixin,
    DetailView
):
    template_name = 'gestao_produto/table_rows/tr_produto_por_lote.html'
    restrict_direct_access = True
    model = ProdutoPorLote
    context_object_name = 'lote'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_context_data_produto(context['lote'])
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class DeleteProdutoPorLoteView(
    UserFromLojaRequiredMixin,
    PermissionRequiredMixin,
    DeleteHTMXView
):
    model = ProdutoPorLote
    form_class = ProdutoPorLoteDeleteForm
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get(self, *args, **kwargs):
        return self.http_method_not_allowed(request=self.request, *args, **kwargs)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'produto': self.object.produto,
            'lote': self.object,
        }

    def form_invalid(self, form):
        # TODO: posteriormente alterar isso para mostrar um erro
        return JsonResponse({'status': True}, status=422)

    def form_valid(self, form):
        self.object.delete()
        return HttpResponse('')


class GestaoProdutosPorLoteView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, DetailView
):
    template_name = 'gestao_produto/gestao_produtos_por_lote.html'
    model = Produto
    context_object_name = 'produto'
    pk_url_kwarg = 'produto_pk'

    usuario_class = GerenteDeEstoque
    permission_required = 'loja.gerir_estoque_de_produto'

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})
