from django.http import HttpRequest, HttpResponse, JsonResponse
from django.core.paginator import Paginator
from django.urls import reverse_lazy
from django.shortcuts import render, redirect

from common.data import DadosPapeis
from saas.models.usuario_contratacao import ClienteContratante, GerenteDeContratos
from saas.views.interfaces import ABCGestaoContratoCRUDListView
from saas.forms import ContratoForm, FiltroContratoForm
from saas.models import Contrato

class GestaoContratoCRUDListView(ABCGestaoContratoCRUDListView):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'lista_contratos.html'
    form_class = ContratoForm
    filter_form = FiltroContratoForm
    model = Contrato
    default_order = ['id']
    paginate_by = 20
    usuario_class = [GerenteDeContratos, ClienteContratante]

    def alterar_status_contrato(self, contrato, ativo: bool) -> None:
        if contrato is None:
            raise Exception('Contrato não encontrado')

        contrato.ativo = ativo
        contrato.save()

    def get_filter_parameters(self):
        parameters = super().get_filter_parameters()

        if 'ativo' in parameters.keys() and parameters['ativo'] == 'todos':
            parameters.pop('ativo')

        return parameters

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page()
        form = self.form_class()
        filter_form = self.filter_form()

        if self.get_user().papel_group().name != DadosPapeis.GERENTE_DE_CONTRATOS:
            # TODO criar página de acesso negado customizada
            return HttpResponseForbidden("Você não tem permissão para acessar esta página.")

        return render(request, self.template_name, {
            'form': form,
            'filter_form': filter_form,
            'contratos': queryset
        })
    
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