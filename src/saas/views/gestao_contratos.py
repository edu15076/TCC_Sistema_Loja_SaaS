from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy
from django.shortcuts import render

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
    object_pk = None
    permission_required = 'saas.gerir_contratos'
    raise_exception = True

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

        return render(
            request,
            self.template_name,
            {
                'form': form,
                'filter_form': filter_form,
                'contratos': queryset,
                'contratos_ativos_count': self.model.contratos.filter(
                    ativo=True
                ).count(),
            },
        )

    def form_valid(self, form):
        contrato = form.save()
        return render(
            self.request,
            'cards/card_contrato.html', {'contrato': contrato, 'success': True}
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
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
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
