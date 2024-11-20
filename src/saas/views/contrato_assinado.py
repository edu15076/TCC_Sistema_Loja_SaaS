from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.views import View
from saas.models.contrato_assinado import ContratoAssinado
from saas.views.interfaces import ABCContratoAssinadoView

class ContratoAssinadoView(ABCContratoAssinadoView, View):
    template_name = 'gestao_cliente_contratante.html'

    def get_contrato_assinado(self, contrato_id=None) -> ContratoAssinado:
        """
        Implementação do método para buscar o contrato assinado vigente do cliente logado.
        Caso contrato_id seja fornecido, retorna um contrato específico, caso contrário, busca o contrato ativo.
        """
        try:
            contrato = ContratoAssinado.objects.get(
                cliente_contratante=self.request.user,
                vigente=True
            )
            return contrato
        except ContratoAssinado.DoesNotExist:
            return None

    def get(self, request: HttpRequest) -> HttpResponse:
        """Exibe os detalhes do contrato assinado vigente"""
        contrato = self.get_contrato_assinado()

        if not contrato:
            messages.error(request, "Nenhum contrato vigente encontrado.")
            return render(request, self.template_name, {
                'mensagem_erro': "Nenhum contrato vigente encontrado."
            })

        # Obtendo os valores para visualização do cliente contratante
        valores = contrato.values_visualizacao_cliente_contratante()

        # Renderizando o template com os valores do contrato
        return render(request, self.template_name, {
            'contrato': contrato,
            'valores': valores,
        })