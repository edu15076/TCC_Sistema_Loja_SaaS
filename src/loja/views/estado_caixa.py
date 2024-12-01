from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from loja.models.caixa import Caixa
from loja.models.fluxodecaixa import FluxoDeCaixa
from loja.views.interfaces.estado_caixa import ABCEstadoCaixaCRUDListView

class EstadoCaixaListView(ABCEstadoCaixaCRUDListView):
    model = Caixa
    template_name = 'estado_caixa.html'
    context_object_name = 'caixas'

    def get_queryset(self):
        loja_scope = self.kwargs.get('loja_scope')
        queryset = Caixa.objects.filter(loja=loja_scope, ativo=True)

        filtro_ativo = self.request.GET.get('filtro', None)
        if filtro_ativo == 'abertos':
            queryset = queryset.filter(horario_aberto__isnull=False)
        elif filtro_ativo == 'fechados':
            queryset = queryset.filter(horario_aberto__isnull=True)

        ordem = self.request.GET.get('ordem', None)
        if ordem == 'numero':
            queryset = queryset.order_by('numero_identificacao')
        elif ordem == 'dinheiro':
            queryset = queryset.order_by('dinheiro_em_caixa')
        elif ordem == 'id':  
            queryset = queryset.order_by('id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_ativo'] = self.request.GET.get('filtro', 'todos')
        context['loja_scope'] = self.kwargs.get('loja_scope')
        context['is_estado_caixa'] = True  
        return context

    def post(self, request, *args, **kwargs):
        caixa_id = request.POST.get('id')
        acao = request.POST.get('acao')

        if caixa_id and acao:
            caixa = Caixa.objects.get(id=caixa_id)

            if acao == 'abrir':
                caixa.horario_aberto = timezone.now()
                caixa.save()
            elif acao == 'fechar':
                fluxo_de_caixa = FluxoDeCaixa(
                    caixa=caixa,
                    horario_aberto=caixa.horario_aberto,  
                    horario_fechado=timezone.now(), 
                    valor_em_caixa=caixa.dinheiro_em_caixa
                )
                fluxo_de_caixa.save() 
                caixa.horario_aberto = None
                caixa.save()

            return redirect('estado_caixa', loja_scope=kwargs.get('loja_scope'))

        return HttpResponse(status=400)

    def get(self, request, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return render(request, self.template_name, context)