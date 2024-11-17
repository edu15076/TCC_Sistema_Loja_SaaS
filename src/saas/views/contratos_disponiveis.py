from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from saas.views.interfaces import ABCContratosDisponiveisCRUDView
from saas.models import Contrato
from saas.forms import FiltroContratosDisponiveisForm


class ContratosDisponiveisCRUDView(ABCContratosDisponiveisCRUDView):
    template_name = 'lista_contratos_disponiveis.html'
    model = Contrato
    filter_form = FiltroContratosDisponiveisForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page().filter(ativo=True)
        filter_form = self.filter_form()

        return render(request, self.template_name, {
            'filter_form': filter_form,
            'contratos': queryset
        })

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return JsonResponse({'success': True}, status=200)
