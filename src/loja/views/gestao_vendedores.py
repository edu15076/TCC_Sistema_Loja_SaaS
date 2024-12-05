from django.http import HttpResponseNotFound, JsonResponse
from django.urls import reverse
from django.views.generic import ListView, DetailView, TemplateView, FormView

from loja.forms.gestao_vendedor_forms import AlterarComissaoVendedorForm
from loja.models import Vendedor, GerenteDeRH
from loja.views import LojaProtectionMixin, UserFromLojaRequiredMixin
from util.views import HTMXHelperMixin, HTMXFormMixin

__all__ = (
    'VendedorContextDataMixin',
    'ListVendedoresView',
    'CardVendedorView',
    'AlterarComissaoVendedorView',
    'GestaoVendedoresView',
)


class VendedorContextDataMixin:
    def pode_alterar_comissao(self, vendedor: Vendedor):
        return vendedor.is_active and vendedor != self.user

    def get_alterar_comissao_form(self, vendedor: Vendedor):
        return AlterarComissaoVendedorForm(
            initial={
                'vendedor': vendedor.pk,
                'comissao': vendedor.porcentagem_comissao,
            },
            disabled=not self.pode_alterar_comissao(vendedor),
            loja=self.user.loja,
            auto_id=f'alterar-comissao-vendedor-{vendedor.pk}-%s'
        )

    def get_context_data_vendedor(self, vendedor: Vendedor) -> Vendedor:
        vendedor.alterar_comissao_form = self.get_alterar_comissao_form(vendedor)
        return vendedor


class ListVendedoresView(
    LojaProtectionMixin, VendedorContextDataMixin, HTMXHelperMixin, ListView
):
    template_name = 'gestao_vendedores/includes/list_vendedores.html'
    model = Vendedor
    # restrict_direct_access = True
    context_object_name = 'vendedores'
    ordering = ['-is_active', '-_porcentagem_comissao', 'nome']

    usuario_class = GerenteDeRH

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for vendedor in context['vendedores']:
            self.get_context_data_vendedor(vendedor)
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class CardVendedorView(
    LojaProtectionMixin, VendedorContextDataMixin, HTMXHelperMixin, DetailView
):
    template_name = 'gestao_vendedores/cards/card_vendedor.html'
    model = Vendedor
    context_object_name = 'vendedor'

    usuario_class = GerenteDeRH

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_context_data_vendedor(context['vendedor'])
        return context

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class AlterarComissaoVendedorView(
    LojaProtectionMixin, HTMXFormMixin, FormView
):
    form_class = AlterarComissaoVendedorForm
    form_template_name: str = (
        'gestao_vendedores/forms/htmx_alterar_comissao_vendedor.html'
    )
    template_name = 'gestao_vendedores/forms/htmx_alterar_comissao_vendedor.html'
    redirect_on_success = False
    success_url = None
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    usuario_class = GerenteDeRH

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {
            'action': reverse('alterar_comissao', kwargs={
                'loja_scope': self.scope.pk,
            }),
        }

    def get_success_url(self):
        success_url = reverse('vendedor_detail', kwargs=self.get_success_url_kwargs())
        return None  # Altere isso se quiser uma atualização do card

    def get_success_url_kwargs(self) -> dict:
        return {
            'pk': self.form.cleaned_data['vendedor'].pk,
            'loja_scope': int(self.user.loja),
        }

    def get_form_kwargs(self) -> dict:
        return super().get_form_kwargs() | {'loja': self.user.loja}

    def get_form(self, form_class=None):
        if not hasattr(self, 'form'):
            setattr(self, 'form', super().get_form(form_class))
        return self.form

    def form_invalid(self, form):
        return super().form_invalid(form)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})


class GestaoVendedoresView(
    UserFromLojaRequiredMixin, TemplateView
):
    template_name = 'gestao_vendedores/gestao_vendedores.html'

    usuario_class = GerenteDeRH

    def get_login_url(self):
        return reverse('login_loja', kwargs={'loja_scope': int(self.scope)})
