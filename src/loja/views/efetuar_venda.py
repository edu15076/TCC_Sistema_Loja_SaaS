from datetime import datetime
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render

from util.mixins import MultipleFormsViewMixin
from loja.models.funcionario import GerenteFinanceiro
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Promocao, Venda, Item, Caixeiro
from loja.views import LojaProtectionMixin
from loja.forms import ItemVendaForm, VendaForm

class EfetuarVendaView(
    MultipleFormsViewMixin,
    LojaProtectionMixin,
    LoginRequiredMixin,
    PermissionRequiredMixin,
    CreateView
):
    login_url = reverse_lazy('login_loja')
    permission_required = 'loja.efetuar_venda'
    raise_exception = True
    template_name = 'efetuar_vendas/efetuar_venda.html'
    model = Venda
    object = None
    usuario_class = Caixeiro
    forms_class = {
        'venda': VendaForm,
        'item_venda': ItemVendaForm,
    }

    def handle_no_permission(self):
        print(self.user)
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        return context
    
    def get_caixa(self):
        return self.user.recuperar_caixa(datetime.now())
    
    def caixa_aberto(self):
        return self.get_caixa() is not None
    
    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = {}
        kwargs['loja'] = self.get_loja()

        if request is not None:
            kwargs['data'] = request.POST
            kwargs['caixeiro'] = self.user

        return kwargs
    
    def get_template_names(self):
        templates = [self.template_name]

        request = self.request
        if self.forms_class['item_venda'].submit_name() in request.POST:
            templates.append('efetuar_vendas/item_venda.html')
        elif self.forms_class['venda'].submit_name() in request.POST:
            templates.append('efetuar_vendas/venda_sucess.html')
            templates.append('efetuar_vendas/venda_fail.html')

        return super().get_template_names()
    
    def form_valid(self, form):
        if form.form_name() == 'venda':
            venda = form.save()

            return render(self.request, self.get_template_names()[1], {'venda': venda})
        else:
            print('aaaaaaaa')
            item = form.save()

            # item

            return render(self.request, self.get_template_names()[1], {'item': item})
        
    
    def get(self, request, *args, **kwargs):
        if not self.caixa_aberto():
            return render(request, 'efetuar_vendas/caixa_fechado.html')
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        print(request.POST)

        if not self.caixa_aberto():
            return JsonResponse({'type':'error', 'message':'Caixa fechado'}, status=400)
        
        return super().post(request, *args, **kwargs)