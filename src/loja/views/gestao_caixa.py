from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now
from django.shortcuts import render

from loja.forms.cadastro_caixa_form import CaixaForm
from loja.models.caixa import Caixa
from loja.views.interfaces.gestao_caixa import ABCGestaoCaixaCRUDListView


class GestaoCaixaView(ABCGestaoCaixaCRUDListView):
    object_list = Caixa.caixas.all()
    template_name = "gestao_caixa.html"

    def get(self, request: HttpRequest, *args, **kwargs):
        caixas = Caixa.caixas.all()
        form = CaixaForm()

        return render(request, self.template_name, {
            'form': form,
            'caixas': caixas,
            'loja_scope': caixas[0].loja.scope_id
        })

    def post(self, request, *args, **kwargs):
        caixa_id = request.POST.get('id')
        status = request.POST.get('ativo')
        caixa = Caixa.caixas.get(id=caixa_id)

        if status == 'false': 
            try:
                caixa.horario_aberto = now()
                caixa.ativo = True
                caixa.save()
                messages.success(request, f"Caixa {caixa.numero_identificacao} aberto com sucesso.")
            except ValueError as e:
                messages.error(request, str(e))
        else: 
            try:
                fluxo = caixa.fechar_caixa()  
                caixa.ativo = False
                caixa.save()
                messages.success(request, f"Caixa {caixa.numero_identificacao} fechado. Fluxo de caixa gerado.")
            except ValueError as e:
                messages.error(request, str(e))

        return render(request, "cards/card_caixa.html", {
            'caixa': caixa,
            'loja_scope': caixa.loja.scope_id
        })