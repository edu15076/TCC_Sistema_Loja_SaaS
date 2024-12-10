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

        if 'error_message' in request.session:
            del request.session['error_message']

        if acao == "adicionar":
            return self.adicionar_caixa(request, loja_scope)
        elif acao == "pesquisar_caixeiro":
            return self.pesquisar_caixeiro(request, loja_scope)
        elif acao == "remover_periodo":
            return self.remover_periodos(request, loja_scope)
        elif caixa_id:
            return self.gerenciar_caixa(request, caixa_id, loja_scope)
        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def adicionar_caixa(self, request, loja_scope):
        numero_identificacao = request.POST.get("numero_identificacao")

        if Caixa.objects.filter(numero_identificacao=numero_identificacao, loja__scope=loja_scope).exists():
            request.session["error_message"] = "Esse número de identificação já está cadastrado nesta loja. Por favor, escolha outro."
            return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

        if not numero_identificacao.isdigit() or len(numero_identificacao) != 8:
            request.session["error_message"] = "O número de identificação deve ter exatamente 8 dígitos."
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
            request.session["success_message"] = "Caixa adicionado com sucesso."
            return redirect(reverse('gestao_caixas', kwargs ={'loja_scope': loja_scope}))
        except IntegrityError:
            request.session["error_message"] = "Já existe um caixa cadastrado com esse número de identificação nesta loja."
            return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def pesquisar_caixeiro(self, request, loja_scope):
        numero_identificacao = request.POST.get("numero_identificacao")
        horario_inicio = request.POST.get("horario_inicio_pesquisa")
        horario_fim = request.POST.get("horario_fim_pesquisa")
        dias_da_semana = request.POST.getlist("dia_da_semana")
        try:
            caixa = get_object_or_404(Caixa, numero_identificacao=numero_identificacao, loja__scope=loja_scope)
            if not caixa.ativo:
                request.session["error_message"] = "O caixa não está ativo."
                return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))
        except Http404:
            request.session["error_message"] = f"O caixa com este número de identificação {numero_identificacao} é inválido."
            return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

        caixeiros_encontrados = TrabalhaCaixa.objects.filter(caixa=caixa)

        if dias_da_semana and "todos" not in dias_da_semana:
            caixeiros_encontrados = caixeiros_encontrados.filter(
                trabalho_por_dia__dia_da_semana__in=[self.get_dia_da_semana(dia) for dia in dias_da_semana],
                trabalho_por_dia__timeslices__start__gte=horario_inicio,
                trabalho_por_dia__timeslices__end__lte=horario_fim,
            )

        if caixeiros_encontrados.exists():
            dias_nomes = {
                0: 'Domingo',
                1: 'Segunda',
                2: 'Terça',
                3: 'Quarta',
                4: 'Quinta',
                5: 'Sexta',
                6: 'Sábado',
            }
            pesquisa_resultado = [
                (f"{trabalho.caixeiro.nome} - {timeslice.start} a {timeslice.end} ({dias_nomes[trabalho.trabalho_por_dia.dia_da_semana]})", trabalho.id) 
                for trabalho in caixeiros_encontrados 
                for timeslice in trabalho.trabalho_por_dia.timeslices.all()
            ]
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
        }
        return render(request, self.template_name, context)

    def remover_periodos(self, request, loja_scope):
        trabalho_ids = request.POST.getlist("trabalho_ids")
        if trabalho_ids:
            try:
                TrabalhaCaixa.objects.filter(id__in=trabalho_ids).delete()
                request.session["success_message"] = "Períodos removidos com sucesso."
            except Exception as e:
                request.session["error_message"] = f"Ocorreu um erro ao remover os períodos: {str(e)}"
        else:
            request.session["error_message"] = "Nenhum período selecionado para remover."
        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def gerenciar_caixa(self, request, caixa_id, loja_scope):
        caixa = get_object_or_404(Caixa, id=caixa_id)
        acao = request.POST.get("acao")

        if acao == "remover":
            caixa.ativo = False
            TrabalhaCaixa.objects.filter(caixa=caixa).delete()
            caixa.save()
        elif acao == "associar_caixeiro":
            return self.associar_caixeiro(request, caixa, loja_scope)

        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def associar_caixeiro(self, request, caixa, loja_scope):
        caixeiro_id = request.POST.get("caixeiro_id")
        horario_inicio = request.POST.get("horario_inicio")
        horario_fim = request.POST.get("horario_fim")
        dias_trabalho = request.POST.getlist("dias_trabalho")
        caixeiro = get_object_or_404(Caixeiro, codigo=caixeiro_id)

        horario_inicio_time = datetime.strptime(horario_inicio, '%H:%M').time()
        horario_fim_time = datetime.strptime(horario_fim, '%H:%M').time()

        for dia in dias_trabalho:
            dia_da_semana = self.get_dia_da_semana(dia)

            trabalhos_existentes = TrabalhaCaixa.objects.filter(
                caixeiro=caixeiro,
                trabalho_por_dia__dia_da_semana=dia_da_semana
            ).prefetch_related('trabalho_por_dia__timeslices')

            for trabalho in trabalhos_existentes:
                for timeslice in trabalho.trabalho_por_dia.timeslices.all():
                    if horario_inicio_time < timeslice.end and horario_fim_time > timeslice.start:
                        request.session["error_message"] = f"O caixeiro {caixeiro.nome} já está alocado em um horário nesse dia."
                        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

            time_slice = TimeSlice.objects.create(start=horario_inicio_time, end=horario_fim_time)
            trabalho_por_dia = TrabalhoPorDia.objects.create(dia_da_semana=dia_da_semana)
            trabalho_por_dia.timeslices.add(time_slice)

            TrabalhaCaixa.objects.create(
                caixeiro=caixeiro,
                caixa=caixa,
                trabalho_por_dia=trabalho_por_dia
            )

        return redirect(reverse('gestao_caixas', kwargs={'loja_scope': loja_scope}))

    def get_dia_da_semana(self, dia):
        if isinstance(dia, int):
            return dia
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

    def get_caixeiros_disponiveis(self, loja_scope):
        return Funcionario.funcionarios.filter(groups__name='loja_caixeiros', scope=loja_scope)

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
        }