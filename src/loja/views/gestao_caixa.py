from datetime import timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.db import IntegrityError  
from loja.models.caixa import Caixa
from loja.models.funcionario import Caixeiro, Funcionario, GerenteDeRH
from loja.models.loja import Loja
from loja.models.trabalhacaixa import TrabalhaCaixa
from loja.models.timeslice import TimeSlice
from loja.models.trabalhapordia import TrabalhoPorDia
from loja.views.interfaces.gestao_caixa import ABCGestaoCaixaCRUDListView

class GestaoCaixaCRUDListView(ABCGestaoCaixaCRUDListView, View):
    template_name = "gestao_caixa.html"
    usuario_class = GerenteDeRH

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        filtro = request.GET.get("filtro", "todos")
        loja_scope = kwargs.get("loja_scope")  
        if filtro == "abertos":
            caixas = Caixa.objects.filter(horario_aberto__isnull=False, ativo=True, loja__scope=loja_scope)  
        elif filtro == "fechados":
            caixas = Caixa.objects.filter(horario_aberto__isnull=True, ativo=True, loja__scope=loja_scope)
        else:
            caixas = Caixa.objects.filter(ativo=True, loja__scope=loja_scope)  
        
        ordem = request.GET.get("ordem", "id")  
        if ordem == "dinheiro_em_caixa":
            caixas = caixas.order_by('-dinheiro_em_caixa') 
        elif ordem == "nome":
            caixas = caixas.order_by('numero_identificacao') 
        else:
            caixas = caixas.order_by(ordem)  

        caixeiros = self.get_caixeiros_disponiveis(loja_scope)

        context = {
            "caixas": caixas,
            "filtro": filtro,
            "ordem": ordem,
            "form": self.get_form(),
            "loja_scope": loja_scope,
            "is_gestao_caixa": True,
            "caixeiros": caixeiros, 
        }
        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        acao = request.POST.get("acao")
        caixa_id = request.POST.get("id")
        loja_scope = kwargs.get("loja_scope")  
        
        if acao == "adicionar":
            numero_identificacao = request.POST.get("numero_identificacao")

            if Caixa.objects.filter(numero_identificacao=numero_identificacao, loja__scope=loja_scope).exists():
                request.session["error_message"] = "Esse número de identificação já está cadastrado. Por favor, escolha outro."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            if not numero_identificacao.isdigit() or len(numero_identificacao) != 8:
                request.session["error_message"] = "O número de identificação deve ter exatamente 8 dígitos."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
            
            if int(numero_identificacao) < 1 or int(numero_identificacao) > 99999999:
                request.session["error_message"] = "O número de identificação deve estar entre 00000001 e 99999999."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            loja = get_object_or_404(Loja, scope=loja_scope)

            try:
                Caixa.objects.create(
                    numero_identificacao=numero_identificacao,
                    horario_aberto=None,
                    dinheiro_em_caixa=0,
                    ativo=True,
                    loja=loja
                )
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
            except IntegrityError:
                request.session["error_message"] = "Já existe um caixa cadastrado com esse número de identificação."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

        if caixa_id:
            caixa = get_object_or_404(Caixa, id=caixa_id)
            try:
                if acao == "abrir":
                    caixa.horario_aberto = timezone.now()  
                    caixa.save()
                elif acao == "fechar":
                    caixa.horario_aberto = None  
                    caixa.save()
                elif acao == "movimentar":
                    valor = request.POST.get("valor", 0.0)
                    caixa.movimentar_dinheiro_em_caixa(float(valor))
                elif acao == "remover":
                    caixa.ativo = False
                    caixa.save()
                elif acao == "associar_caixeiro":
                    caixeiro_id = request.POST.get("caixeiro_id")
                    horario_inicio = request.POST.get("horario_inicio")
                    horario_fim = request.POST.get("horario_fim")
                    dias_trabalho = request.POST.getlist("dias_trabalho")   
                    caixeiro = get_object_or_404(Caixeiro, id=caixeiro_id)

                    for dia in dias_trabalho:
                        dia_da_semana = self.get_dia_da_semana(dia)
                        trabalhos_existentes = TrabalhaCaixa.objects.filter(
                            caixeiro=caixeiro,
                            trabalho_por_dia__dia_da_semana=dia_da_semana
                        ).prefetch_related('trabalho_por_dia__timeslices')

                        for trabalho in trabalhos_existentes:
                            for timeslice in trabalho.trabalho_por_dia.timeslices.all():
                                if (horario_inicio < timeslice.end and horario_fim > timeslice.start):
                                    request.session["error_message"] = f"O caixeiro {caixeiro.nome} já está associado a um horário nesse dia."
                                    return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

                    time_slice = TimeSlice.objects.create(start=horario_inicio, end=horario_fim)

                    for dia in dias_trabalho:
                        dia_da_semana = self.get_dia_da_semana(dia)  
                        trabalho_por_dia = TrabalhoPorDia.objects.create(dia_da_semana=dia_da_semana)
                        trabalho_por_dia.timeslices.add(time_slice)

                        TrabalhaCaixa.objects.create(
                            caixeiro=caixeiro,
                            caixa=caixa,
                            trabalho_por_dia=trabalho_por_dia
                        )

                elif acao == "pesquisar_caixeiro":
                    numero_identificacao = request.POST.get("numero_identificacao")
                    horario_inicio = request.POST.get("horario_inicio_pesquisa")
                    horario_fim = request.POST.get("horario_fim_pesquisa")

                    caixeiros_encontrados = TrabalhaCaixa.objects.filter(
                        caixa=caixa,
                        trabalho_por_dia__timeslices__start__gte=horario_inicio,
                        trabalho_por_dia__timeslices__end__lte=horario_fim,
                    )

                    if numero_identificacao:
                        caixa_pesquisa = get_object_or_404(Caixa, numero_identificacao=numero_identificacao, loja__scope=loja_scope)
                        caixeiros_encontrados = caixeiros_encontrados.filter(caixa=caixa_pesquisa)

                    if caixeiros_encontrados.exists():
                        pesquisa_resultado = [trabalho.caixeiro.nome for trabalho in caixeiros_encontrados]
                        mensagem_resultado = "Caixeiros encontrados."
                    else:
                        pesquisa_resultado = None
                        mensagem_resultado = "Nenhum caixeiro encontrado."

                    context = {
                        "caixas": Caixa.objects.filter(ativo=True, loja__scope=loja_scope),
                        "loja_scope": loja_scope,
                        "pesquisa_resultado": pesquisa_resultado,
                        "mensagem_resultado": mensagem_resultado,
                        "caixa": caixa,
                        "filtro": request.GET.get("filtro", "todos"),
                        "ordem": request.GET.get("ordem", "id"),
                        "form": self.get_form(),
                        "is_gestao_caixa": True,
                        "caixeiros": self.get_caixeiros_disponiveis(loja_scope),
                    }
                    return render(request, self.template_name, context)

                else:
                    raise ValueError("Ação inválida.")
            except ValueError as e:
                request.session["error_message"] = str(e)

        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def get_dia_da_semana(self, dia):
        dias = {
            'domingo': 0,
            'segunda': 1,
            'terca': 2,
            'quarta': 3,
            'quinta': 4,
            'sexta': 5,
            'sabado': 6,
        }
        return dias.get(dia.lower())

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
        }
    
    def get_caixeiros_disponiveis(self, loja_scope):
        return Funcionario.funcionarios.filter(groups__name='loja_caixeiros', scope=loja_scope)