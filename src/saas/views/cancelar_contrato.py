from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from saas.models.contrato_assinado import ContratoAssinado

class CancelarContratoView(View):
    template_name = 'card_cancelar_contrato.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Renderiza o card de cancelamento do contrato com cálculo de multa.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

        contrato_assinado = ContratoAssinado.objects.filter(
            cliente_contratante=request.user,
            vigente=True
        ).first()

        if not contrato_assinado:
            return redirect('contratos_disponiveis')  # Redireciona para a página de contratos disponíveis

        try:
            # Cálculo da multa
            multa = contrato_assinado.calcular_multa(
                valor_por_periodo=contrato_assinado.contrato.valor_por_periodo,
                taxa_de_multa=contrato_assinado.contrato.taxa_de_multa,
                total_periodos=contrato_assinado.contrato.periodo.tempo_total.days
            )
        except AttributeError as e:
            return JsonResponse({'error': 'Erro ao calcular a multa. Verifique os dados do contrato.', 'details': str(e)}, status=500)

        return render(request, self.template_name, {
            'contrato': contrato_assinado,
            'multa': multa,
        })

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Cancela o contrato assinado.
        """
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Usuário não autenticado'}, status=401)

        contrato_assinado = get_object_or_404(
            ContratoAssinado,
            cliente_contratante=request.user,
            vigente=True
        )

        contrato_assinado.vigente = False
        contrato_assinado.save()

        return JsonResponse({'message': 'Contrato cancelado com sucesso!'}, status=200)