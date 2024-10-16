from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse

from util.views.filter_list import FilterListView


class ABCHistoricoPagamentosView(ABC, FilterListView):
    @abstractmethod
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        """
        Recebe a solicitação GET e carrega os pagamentos
        com filtros aplicados, se houver filtros preenchidos

        :param request: Uma extrutura HttpRequest contendo
        os seguites campos, preenchidos ou não.
        - `estado`: informa se o pagamento esta pendente,
          atrasado ou quitado
        - `data_pagamento`: quando o pagamento foi registrado
        - `periodo`: informa em qual periodo interessa buscar
          os pagamentos
        - `tipo`: se é um pagamento comum ou multa

        :type request: `HttpResponse`

        :return: Um `HttpResponse` contendo, no `context`:
        - `estado`
        - `data_pagamento`
        - `data_inicio_prazo`
        - `data_fim_prazo`
        - `tipo`
        ? questionar como é a questão do comprovante do pagamento

        :rtype: `HttpResponse`
        """
