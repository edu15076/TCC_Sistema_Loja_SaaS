from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.utils.timezone import now

from loja.forms.cadastrocaixaform import CaixaForm
from loja.models.caixa import Caixa
from loja.views.interfaces.gestaocaixa import ABCGestaoCaixaCRUDListView

class GestaoCaixaView(ABCGestaoCaixaCRUDListView):
    def get(self, request, *args, **kwargs):
        # Filtragem de caixas (ativos ou inativos)
        ordem = request.GET.get('ordem', 'numero_identificacao')
        filtro = request.GET.get('filtro', 'ativo')
        caixas = Caixa.objects.filter(ativo=filtro == 'ativo').order_by(ordem)

        form = CaixaForm()

        context = {
            'caixas': caixas,
            'form': form,
        }

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        acao = request.POST.get('acao')
        caixa_id = request.POST.get('id')
        caixa = get_object_or_404(Caixa, id=caixa_id)

        if acao == 'abrir':
            if caixa.ativo:
                messages.error(request, "O caixa já está aberto.")
            else:
                caixa.horario_aberto = now()
                caixa.ativo = True
                caixa.save()
                messages.success(request, f"Caixa {caixa.numero_identificacao} aberto com sucesso.")
        
        elif acao == 'fechar':
            try:
                fluxo = caixa.fechar_caixa()
                messages.success(request, f"Caixa {caixa.numero_identificacao} fechado. Fluxo de caixa gerado.")
            except ValueError as e:
                messages.error(request, str(e))
        
        elif acao == 'movimentar':
            valor = float(request.POST.get('valor'))
            try:
                caixa.movimentar_dinheiro_em_caixa(valor)
                messages.success(request, f"Dinheiro movimentado no caixa {caixa.numero_identificacao}.")
            except ValueError as e:
                messages.error(request, str(e))
        
        return redirect('caixa_list')