from abc import ABC, abstractmethod

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest, HttpResponse
from django.views import View

from common.views.mixins import UsuarioMixin
from ...models import ContratoAssinado

__all__ = (
    'ABCCancelarContratoAssinado',
)

class ABCContratoAssinadoView(
    ABC, LoginRequiredMixin, UsuarioMixin, View
):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe solicitação de carregar a página com o dado do contrato assinado 
        (vigente) do gerente contratante logado.
        """
        contrato_assinado = self.get_contrato_assinado()
        return HttpResponse(self.template_name, content={
            'contrato_assinado': contrato_assinado.values_visualizacao_cliente_contratante()
        })
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações dos estados dos contratos (criações, deleções, atualizações)
        """
        action = request.POST.get('action')
        contrato_id = request.POST.get('id')
        
        if action == 'cancelar':
            contrato_assinado = self.get_contrato_assinado(contrato_id)
            # Lógica para cancelar o contrato
            contrato_assinado.cancelar()  # Supondo que exista um método 'cancelar' no modelo ContratoAssinado
            return HttpResponse("Contrato cancelado com sucesso")
        
        # Caso contrário, realiza outras ações de criação, edição, etc.
        return super().post(request, *args, **kwargs)
    
    @abstractmethod
    def get_contrato_assinado(self, contrato_id=None) -> ContratoAssinado:
        """
        Este método deve ser implementado em uma subclasse para retornar o contrato assinado
        """
        raise NotImplementedError()