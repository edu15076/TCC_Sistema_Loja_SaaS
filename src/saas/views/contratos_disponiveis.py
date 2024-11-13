from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from saas.views.interfaces import ABCContratosDisponiveisCRUDView
from saas.models import Contrato


class ContratosDisponiveisCRUDView(ABCContratosDisponiveisCRUDView):
    template_name = 'lista_contratos_disponiveis.html'
    model = Contrato

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page().filter(ativo=True)

        return render(request, self.template_name, {'contratos': queryset})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return JsonResponse({'success': True}, status=200)
