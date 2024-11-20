from django.http import HttpRequest, HttpResponse, JsonResponse, HttpResponseForbidden
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
    object_pk = None

    def get_pk_slug(self) -> tuple[int | None, str | None]:
        return self.object_pk, None

    def alterar_status_contrato(self, contrato) -> None:
        if contrato is None:
            raise Exception('Contrato não encontrado')

        contrato.ativo = not contrato.ativo
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

        # TODO impedir acesso não autorizado
        if self.user.papel_group.name != DadosPapeis.GERENTE_DE_CONTRATOS:
            # TODO criar página de acesso negado customizada
            return HttpResponseForbidden(
                "Você não tem permissão para acessar esta página."
            )

        return render(
            request,
            self.template_name,
            {'form': form, 'filter_form': filter_form, 'contratos': queryset, 'contratos_ativos_count': Contrato.contratos.filter(ativo=True).count()},
        )

    def form_valid(self, form):
        contrato = form.save()
        return render(
            self.request, 'card_contrato.html', {'contrato': contrato, 'success': True}
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # TODO impedir acesso não autorizado
        if self.user.papel_group.name != DadosPapeis.GERENTE_DE_CONTRATOS:
            #     # TODO retornar erro 403
            return JsonResponse(
                {
                    'success': False,
                    'error': 'Você não tem permissão para acessar esta página.',
                },
                status=403,
            )

        try:
            self.object_pk = request.POST.get('id')
            contrato = self.get_object()

            if contrato is None:
                return super().post(request, *args, **kwargs)
            else:
                self.alterar_status_contrato(contrato)
                return JsonResponse(
                    {'success': True, 'ativo': contrato.ativo}, status=200
                )

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

        return JsonResponse({'success': True}, status=200)
