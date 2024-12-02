from datetime import datetime, timezone
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.db import IntegrityError  
from django.http import Http404
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

        error_message = request.session.pop('error_message', None)
        success_message = request.session.pop('success_message', None)

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
            "pesquisa_resultado": None,
            "error_message": error_message,  
            "success_message": success_message, 
        }

        return render(request, self.template_name, context)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        acao = request.POST.get("acao")
        caixa_id = request.POST.get("id")
        loja_scope = kwargs.get("loja_scope")  
        #print(acao)
        if 'error_message' in request.session:
            del request.session['error_message']

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

        elif acao == "pesquisar_caixeiro":
            numero_identificacao = request.POST.get("numero_identificacao")
            horario_inicio = request.POST.get("horario_inicio_pesquisa")
            horario_fim = request.POST.get("horario_fim_pesquisa")
            dia_da_semana_str = request.POST.get("dia_da_semana")  

            try:
                caixa = get_object_or_404(Caixa, numero_identificacao=numero_identificacao)
                if not caixa.ativo:
                    request.session["error_message"] = "O caixa não está ativo."
                    return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
            except Http404:
                request.session["error_message"] = f"O caixa com este número de identificação {numero_identificacao} é inválido."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            if dia_da_semana_str == "todos":
                caixeiros_encontrados = TrabalhaCaixa.objects.filter(
                    caixa=caixa,
                    trabalho_por_dia__timeslices__start__gte=horario_inicio,
                    trabalho_por_dia__timeslices__end__lte=horario_fim,
                )
            else:
                dia_da_semana = self.get_dia_da_semana(dia_da_semana_str)
                caixeiros_encontrados = TrabalhaCaixa.objects.filter(
                    caixa=caixa,
                    trabalho_por_dia__dia_da_semana=dia_da_semana,
                    trabalho_por_dia__timeslices__start__gte=horario_inicio,
                    trabalho_por_dia__timeslices__end__lte=horario_fim,
                )

            if numero_identificacao:
                caixa_pesquisa = get_object_or_404(Caixa, numero_identificacao=numero_identificacao, loja__scope=loja_scope)
                caixeiros_encontrados = caixeiros_encontrados.filter(caixa=caixa_pesquisa)

            if caixeiros_encontrados.exists():
                pesquisa_resultado = []
                for trabalho in caixeiros_encontrados:
                    for timeslice in trabalho.trabalho_por_dia.timeslices.all():
                        dia_da_semana = self.get_dia_da_semana(trabalho.trabalho_por_dia.dia_da_semana)
                        resultado_display = f"{trabalho.caixeiro.nome} - {timeslice.start} a {timeslice.end} ({dia_da_semana})"
                        pesquisa_resultado.append((resultado_display, trabalho.id))
                mensagem_resultado = "Caixeiros encontrados."
            else:
                pesquisa_resultado = False
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
                'caixeiro_padrao': self.get_caixeiros_disponiveis(loja_scope).first(),
            }
            return render(request, self.template_name, context)
        
        elif acao == "remover_periodo":
            trabalho_id = request.POST.get("trabalho_id")
            trabalho = get_object_or_404(TrabalhaCaixa, id=trabalho_id)
            try:
                trabalho.delete()
                request.session["success_message"] = "Período removido com sucesso."
            except Exception as e:
                request.session["error_message"] = "Ocorreu um erro ao remover o período."
            
            return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
        
        elif caixa_id:
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
                    TrabalhaCaixa.objects.filter(caixa=caixa).delete()
                    caixa.save()
                elif acao == "associar_caixeiro":
                    caixeiro_id = request.POST.get("caixeiro_id")
                    horario_inicio = request.POST.get("horario_inicio")
                    horario_fim = request.POST.get("horario_fim")
                    dias_trabalho = request.POST.getlist("dias_trabalho")   
                    caixeiro = get_object_or_404(Caixeiro, codigo=caixeiro_id)

                    for dia in dias_trabalho:
                        dia_da_semana = self.get_dia_da_semana(dia)
                        trabalhos_existentes = TrabalhaCaixa.objects.filter(
                            caixeiro=caixeiro,
                            trabalho_por_dia__dia_da_semana=dia_da_semana
                        ).prefetch_related('trabalho_por_dia__timeslices')

                        horario_inicio_time = datetime.strptime(horario_inicio, '%H:%M').time()
                        horario_fim_time = datetime.strptime(horario_fim, '%H:%M').time()

                        for trabalho in trabalhos_existentes:
                            for timeslice in trabalho.trabalho_por_dia.timeslices.all():
                                if (horario_inicio_time < timeslice.end and horario_fim_time > timeslice.start):
                                    request.session["error_message"] = f"O caixeiro {caixeiro.nome} já está associado a um horário nesse dia."
                                    return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

                    time_slice = TimeSlice.objects.create(start=horario_inicio_time, end=horario_fim_time)

                    for dia in dias_trabalho:
                        dia_da_semana = self.get_dia_da_semana(dia)  
                        trabalho_por_dia = TrabalhoPorDia.objects.create(dia_da_semana=dia_da_semana)
                        trabalho_por_dia.timeslices.add(time_slice)

                        TrabalhaCaixa.objects.create(
                            caixeiro=caixeiro,
                            caixa=caixa,
                            trabalho_por_dia=trabalho_por_dia
                        )
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
        
        dias_reverse = {v: k for k, v in dias.items()}

        if isinstance(dia, str):
            return dias.get(dia.lower())
        elif isinstance(dia, int):
            return dias_reverse.get(dia)
        else:
            return None
    
    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
        }
    
    def get_caixeiros_disponiveis(self, loja_scope):
        return Funcionario.funcionarios.filter(groups__name='loja_caixeiros', scope=loja_scope)