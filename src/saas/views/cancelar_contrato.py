from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View

from saas.models.contrato_assinado import ContratoAssinado

class CancelarContratoView(View):
    template_name = 'card_cancelar_contrato.html'

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Renderiza o card de cancelamento do contrato.
        """
        # Utiliza get_object_or_404 para obter o contrato assinado vigente
        contrato_assinado = ContratoAssinado.objects.filter(
            cliente_contratante=request.user,
            vigente=True
        ).first()

        if not contrato_assinado:
            # Caso não haja contrato vigente, redireciona para página de contratos disponíveis
            return redirect('contratos_disponiveis')

        # Renderiza o card com o contrato
        return render(request, self.template_name, {'contrato': contrato_assinado})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Cancela o contrato assinado.
        """
        # Utiliza get_object_or_404 para obter o contrato assinado vigente
        contrato_assinado = get_object_or_404(
            ContratoAssinado,
            cliente_contratante=request.user,
            vigente=True
        )

        # Cancela o contrato
        contrato_assinado.vigente = False
        contrato_assinado.save()

        # Retorna uma resposta de sucesso em formato JSON
        return JsonResponse({'message': 'Contrato cancelado com sucesso!'}, status=200)

    def handle_no_permission(self):
        """
        Caso o usuário não tenha permissão para acessar o contrato,
        redireciona para página de erro ou para página de contratos disponíveis.
        """
        return redirect('contratos_disponiveis')