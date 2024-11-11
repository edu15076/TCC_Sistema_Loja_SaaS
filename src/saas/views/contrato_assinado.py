from abc import ABC, abstractmethod

from django.http import HttpRequest, HttpResponse
from django.views.generic import ListView, CreateView
from django.views.generic.edit import DeletionMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.detail import DetailView
from django.shortcuts import render, redirect

from common.views.mixins import UsuarioMixin
from saas.models.contrato import Contrato
from saas.models.contrato_assinado import ContratoAssinado
from saas.views.interfaces import ABCCancelarContratoAssinado
from .interfaces import ABCContratoAssinadoView

class ContratoAssinadoView(ABCContratoAssinadoView):
    template_name = 'gestao_cliente_contratante.html'

    def get_contrato_assinado(self):
        return ContratoAssinado.contratos_assinados.get(cliente_contratante=self.get_user(), vigente=True)

    # def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
    #     queryset = self.get_page()
    #     form = self.form_class()
        
    #     return render(request, self.template_name, {
    #         'form': form,
    #         'contrato': queryset
    #     })
    
    # def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:

    #     return super().post(request, *args, **kwargs)
    
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     usuario = UsuarioMixin.get_user()
    #     usuario
    #     context["contrato"]
    #     context["contrato"] 
    #     return context


class CancelarContratoAssinado(ABCCancelarContratoAssinado):
    template_name = 'card_cancelar_contrato.html'

    def get(self, request):
        """Carrega o card de cancelamento do contrato"""
        pass

    def post(self, request):
        """Cancela o contrato"""
        pass
    