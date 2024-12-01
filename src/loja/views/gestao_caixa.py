from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from loja.models.caixa import Caixa
from loja.models.funcionario import GerenteDeRH
from loja.models.loja import Loja
from loja.views.interfaces.gestao_caixa import ABCGestaoCaixaCRUDListView
from loja.views.mixins import UserFromLojaRequiredMixin

class GestaoCaixaCRUDListView(ABCGestaoCaixaCRUDListView, View):
    template_name = "gestao_caixa.html"
    usuario_class = GerenteDeRH

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        filtro = request.GET.get("filtro", "todos")
        
        if filtro == "abertos":
            caixas = Caixa.objects.filter(horario_aberto__isnull=False, ativo=True)  
        elif filtro == "fechados":
            caixas = Caixa.objects.filter(horario_aberto__isnull=True, ativo=True)
        else:
            caixas = Caixa.objects.filter(ativo=True)  
        
        ordem = request.GET.get("ordem", "id")  
        if ordem == "dinheiro_em_caixa":
            caixas = caixas.order_by('-dinheiro_em_caixa') 
        elif ordem == "nome":
            caixas = caixas.order_by('numero_identificacao') 
        else:
            caixas = caixas.order_by(ordem)  

        context = {
            "caixas": caixas,
            "filtro": filtro,
            "ordem": ordem,
            "form": self.get_form(),
            "loja_scope": kwargs.get("loja_scope"),
            "is_gestao_caixa": True, 
        }
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        acao = request.POST.get("acao")
        caixa_id = request.POST.get("id")
        valor = request.POST.get("valor", 0.0)
        loja_scope = kwargs.get("loja_scope")  

        if acao == "adicionar":
            numero_identificacao = request.POST.get("numero_identificacao")

            if not numero_identificacao.isdigit() or len(numero_identificacao) != 8:
                request.session["error_message"] = "O número de identificação deve ter exatamente 8 dígitos."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
            
            if int(numero_identificacao) < 1 or int(numero_identificacao) > 99999999:
                request.session["error_message"] = "O número de identificação deve estar entre 00000001 e 99999999."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            if Caixa.objects.filter(numero_identificacao=numero_identificacao, loja__scope=loja_scope).exists():
                request.session["error_message"] = "Já existe um caixa cadastrado com esse número de identificação."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            loja = get_object_or_404(Loja, scope=loja_scope)

            Caixa.objects.create(
                numero_identificacao=numero_identificacao,
                horario_aberto=None,
                dinheiro_em_caixa=0,
                ativo=True,
                loja=loja
            )
            return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

        if caixa_id:
            caixa = get_object_or_404(Caixa, id=caixa_id)
            try:
                if acao == "abrir":
                    caixa.is_open = True
                    caixa.save()
                elif acao == "fechar":
                    caixa.fechar_caixa()
                elif acao == "movimentar":
                    caixa.movimentar_dinheiro_em_caixa(float(valor))
                elif acao == "remover":
                    caixa.ativo = False
                    caixa.save()
                else:
                    raise ValueError("Ação inválida.")
            except ValueError as e:
                request.session["error_message"] = str(e)

        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
        }