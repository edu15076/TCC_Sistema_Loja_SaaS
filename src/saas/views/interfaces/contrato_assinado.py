from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View

from common.views.mixins import UsuarioMixin

from ...models import ContratoAssinado

__all__ = (
    'ABCGestaoContratoCRUDListView',
    'ABCCancelarContratoAssinado',
)

class ABCContratoAssinadoView(
    ABC, LoginRequiredMixin, UsuarioMixin, View
):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe solicitação de carregar a página com o dado do contrato assinado 
        (vigente) do gerente contratante logado.
        
        :param request: pode conter os seguintes campos de filtro
        - `filtro`: um valor que informa se será exibido o contrato ativo 
            ou inativo
        - `page`: retorna a respectiva pagina.
        
        :type request: HttpRequest
        :return: um `context` contendo:
            // - `usuario`
            - `contrato: contrato assinado
            - `form`: formulário de cancelamento do contrato
        :rtype: HttpResponse
        """
        return HttpResponse(self.template_name, content={
            'contrato_assinado': self.get_contrato_assinado().values_visualizacao_cliente_contratante()
        })
    
    @abstractmethod
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe as alterações dos estados dos contratos (criações, deleções
        atualizações)

        :param request: deve conter os seguintes campos:
        //- `action`: informa a ação realizada;

        pode conter os seguintes campos:
        - `id`: o id do contrato será alterado, no caso o estado dele;

        :type request: HttpRequest
        :return: Resultado da operação.
        :rtype: HttpResponse
        """
        return super().post(request, *args, **kwargs)
    
    @abstractmethod
    def get_contrato_assinado(self) -> ContratoAssinado:
        return NotImplementedError()


class ABCCancelarContratoAssinado(View):
    pass
