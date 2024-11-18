from abc import ABC, abstractmethod
from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import View
from common.views.mixins import UsuarioMixin
from ...models import ContratoAssinado

__all__ = (
    'ABCGestaoContratoCRUDListView',
    'ABCCancelarContratoAssinado',
)

class ABCCancelarContratoView(
    ABC, LoginRequiredMixin, UsuarioMixin, View
):
    @abstractmethod
    def get_contrato_assinado(self, contrato_id=None) -> ContratoAssinado:
        """
        Este método deve ser implementado nas subclasses para retornar o contrato assinado.
        """
        raise NotImplementedError()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação de carregar a página com o dado do contrato assinado (vigente)
        do gerente contratante logado.
        """
        contrato_assinado = self.get_contrato_assinado()
        return HttpResponse(self.template_name, content={
            'contrato_assinado': contrato_assinado.values_visualizacao_cliente_contratante()
        })
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações nos estados dos contratos (criações, deleções, atualizações).
        """
        action = request.POST.get('action')
        contrato_id = request.POST.get('id')
        
        if action == 'cancelar':
            contrato_assinado = self.get_contrato_assinado(contrato_id)
            if contrato_assinado:
                contrato_assinado.cancelar()  # Supondo que exista um método 'cancelar' no modelo ContratoAssinado
                return HttpResponse("Contrato cancelado com sucesso")
            else:
                return HttpResponse("Contrato não encontrado ou não ativo.", status=404)
        
        # Caso contrário, realiza outras ações de criação, edição, etc.
        return super().post(request, *args, **kwargs)

class ABCCancelarContratoAssinado(ABCCancelarContratoView):
    template_name = 'cards/card_cancelar_contrato.html'

    def get_contrato_assinado(self, contrato_id=None) -> ContratoAssinado:
        """
        Retorna o contrato assinado do banco de dados. Caso 'contrato_id' seja fornecido,
        ele irá buscar um contrato específico.
        """
        if contrato_id:
            # Usar get_object_or_404 para retornar 404 caso o contrato não seja encontrado
            return get_object_or_404(ContratoAssinado, id=contrato_id)
        return ContratoAssinado.objects.filter(ativo=True).first()  # Retorna o contrato ativo, caso não haja id fornecido.
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Lógica de cancelamento do contrato.
        """
        contrato_id = request.POST.get('id')
        contrato_assinado = self.get_contrato_assinado(contrato_id)
        
        if contrato_assinado:
            if contrato_assinado.vigente:  # Verifica se o contrato está ativo antes de cancelar
                contrato_assinado.cancelar()  # Supondo que você tenha um método 'cancelar' no modelo ContratoAssinado
                return HttpResponse("Contrato cancelado com sucesso")
            else:
                return HttpResponse("Este contrato já foi cancelado.", status=400)
        
        return HttpResponse("Contrato não encontrado ou não ativo.", status=404)