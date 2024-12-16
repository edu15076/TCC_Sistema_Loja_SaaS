from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.template.loader import render_to_string

from util.mixins import MultipleFormsViewMixin
from loja.models.funcionario import GerenteFinanceiro
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Promocao, Venda, Item, Caixeiro, ProdutoPorLote
from loja.views import LojaProtectionMixin
from loja.forms import (
    ItemVendaForm,
    VendaForm,
    ProdutoVendaForm,
    ItensFormSet,
    FormSetHelper,
)
from django.forms import modelformset_factory, formset_factory


class EfetuarVendaView(
    MultipleFormsViewMixin,
    LojaProtectionMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView,
):
    login_url = reverse_lazy('login_loja')
    permission_required = 'loja.efetuar_venda'
    raise_exception = True
    template_name = 'efetuar_vendas/efetuar_venda.html'
    model = Venda
    object = None
    usuario_class = Caixeiro
    forms_class = {
        'produto_venda': ProdutoVendaForm,
        'venda': VendaForm,
        'item_venda': ItemVendaForm,
    }

    def get_forms(self, request: HttpRequest = None):
        forms = {}

        for key, form in self.forms_class.items():
            if key == 'item_venda':
                continue
            forms[key] = self.get_form(form_class=form, request=request)

        return forms

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        return context

    def get_caixa(self):
        return self.user.recuperar_caixa(datetime.now())

    def caixa_aberto(self):
        return self.get_caixa().is_open

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = {}
        kwargs['loja'] = self.get_loja()

        if request is not None:
            kwargs['data'] = request.POST

        if form_class == self.forms_class['venda']:
            kwargs['caixeiro'] = self.user

        return kwargs

    def get_template_names(self):
        templates = [self.template_name]

        request = self.request
        if self.forms_class['produto_venda'].submit_name() in request.POST:
            templates.append('efetuar_vendas/modais/quantidade_lotes_modal.html')
        elif 'quantidade_lotes_submit' in request.POST:
            templates.append('efetuar_vendas/linhas/linha_produto.html')
            templates.append('efetuar_vendas/linhas/linha_form_item.html')
        elif self.forms_class['venda'].submit_name() in request.POST:
            templates.append('efetuar_vendas/modais/venda_sucess.html')
            templates.append('efetuar_vendas/modais/venda_fail.html')

        return templates

    def get_formset_lotes(self, produto):
        form_kwargs = self.get_form_kwargs(
            form_class=ItemVendaForm, request=self.request
        )
        form_kwargs.pop('data')
        lotes = produto.lotes.filter(qtd_em_estoque__gt=0)
        formset = ItensFormSet(
            initial=[
                {'lote': lote.id, 'lote_descricao': lote.lote, 'quantidade': 0}
                for lote in lotes
            ],
            form_kwargs=form_kwargs,
        )
        return formset

    def form_valid(self, form):
        if form.form_name() == 'venda_form':
            venda = form.save()

            return render(self.request, self.get_template_names()[1], {'venda': venda})
        elif form.form_name() == 'produto_venda_form':
            produto = form.save()
            return render(
                self.request,
                self.get_template_names()[1],
                {
                    'quantidade_lotes_formset': self.get_formset_lotes(produto),
                    'quantidade_lotes_helper': FormSetHelper('quantidade_lotes'),
                },
            )
        elif form.form_name() == 'item_venda_form':
            item = form.save()

            return render(self.request, self.get_template_names()[1], {'item': item})
        
    def itens_context(self, itens):
        context = {}
        context['quantidade'] = 0
        context['preco_total'] = 0
        for item in itens:
            context['quantidade'] += item.quantidade
            context['preco_total'] += item.preco_total
        context['produto'] = itens[0].produto

        return context

    def processar_formset(self, request):
        formset = ItensFormSet(request.POST, form_kwargs={'loja': self.get_loja()})

        if formset.is_valid():
            itens_json = []
            itens = []
            preco_total = 0
            desconto_total = 0
            preco_final = 0

            for form in formset:
                item = form.save()

                if item is None:
                    continue

                itens.append(item)
                itens_json.append({'lote': item.lote.pk, 'quantidade': item.quantidade, 'produto': item.produto.pk})
                preco_total += item.produto.preco_de_venda * item.quantidade
                desconto_total += item.produto.calcular_desconto()
                preco_final += item.preco_total

            templates = self.get_template_names()            
            linha_tabela_item = render_to_string(
                templates[1], context=self.itens_context(itens)
            )
            linha_tabela_form_item = render_to_string(
                templates[2], context=self.itens_context(itens)
            )

            return JsonResponse(
                {
                    'type': 'success',
                    'itens': itens_json,
                    'preco_total': preco_total,
                    'desconto_total': desconto_total,
                    'preco_final': preco_final,
                    'linha_tabela_item': linha_tabela_item,
                    'linha_tabela_form_item': linha_tabela_form_item,
                    'message': 'Itens adicionados com sucesso.',
                }
            )
        else:
            return JsonResponse(
                {'type': 'error', 'message': formset.errors}, status=400
            )
        
    def form_invalid(self, form):
        return JsonResponse(
                {'type': 'error', 'message': form.errors}, status=400
            )

    def get(self, request, *args, **kwargs):
        try:
            if not self.caixa_aberto():
                return render(request, 'efetuar_vendas/caixa_fechado.html')
        except AttributeError:
            return render(request, 'efetuar_vendas/caixeiro_nao_alocado.html')
        
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        if not self.caixa_aberto():
            return JsonResponse(
                {'type': 'error', 'message': 'Caixa fechado'}, status=400
            )

        if 'quantidade_lotes_submit' in request.POST:
            return self.processar_formset(request)

        return super().post(request, *args, **kwargs)
