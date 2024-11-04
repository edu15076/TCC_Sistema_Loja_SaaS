from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from saas.views.interfaces import ABCGestaoContratoCRUDListView
from saas.forms import ContratoForm

class GestaoContratoCRUDListView(ABCGestaoContratoCRUDListView):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'lista_contratos.html'
    form_class = ContratoForm
    paginate_by = 20

    def alterar_status_contrato(self, contrato, ativo: bool) -> None:
        if contrato is None:
            raise Exception('Contrato não encontrado')

        contrato.ativo = ativo
        contrato.save()

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page()
        form = self.form_class()

        return render(request, self.template_name, {
            'form': form,
            'contratos': queryset
        })
    
    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        contrato = self.get_object()

        try:
            contrato.delete()

            return JsonResponse({'success': True}, status=204)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            operacao = request.POST.get('operacao')

            if operacao == 'ativar_contrato':
                contrato = self.get_object()
                self.alterar_status_contrato(contrato, True)
            elif operacao == 'desativar_contrato':
                contrato = self.get_object()
                self.alterar_status_contrato(contrato, False)
            else:
                return super().post(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        
        return JsonResponse({'success': True}, status=200)