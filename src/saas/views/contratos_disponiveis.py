from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect

from saas.views.interfaces import ABCContratosDisponiveisCRUDView
from saas.models import Contrato
from saas.forms import FiltroContratosDisponiveisForm
from saas.models import ContratoAssinado
from saas.forms import ContratoAssinadoForm
from common.models import UsuarioGenericoPessoaJuridica


class ContratosDisponiveisCRUDView(ABCContratosDisponiveisCRUDView):
    template_name = 'lista_contratos_disponiveis.html'
    model = Contrato
    filter_form = FiltroContratosDisponiveisForm

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        queryset = self.get_page().filter(ativo=True)
        filter_form = self.filter_form()

        cliente_contratante = UsuarioGenericoPessoaJuridica.usuarios.get(
            cnpj=self.user.codigo
        )

        possui_contrato = ContratoAssinado.contratos_assinados.filter(
            cliente_contratante=cliente_contratante
        ).exists()

        return render(
            request,
            self.template_name,
            {
                'filter_form': filter_form,
                'contratos': queryset,
                'possui_contrato': possui_contrato,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        contrato_id = request.POST.get('contrato_id')
        cnpj = self.user.codigo

        contrato = Contrato.contratos.get(id=contrato_id)
        cliente_contratante = UsuarioGenericoPessoaJuridica.usuarios.get(cnpj=cnpj)

        form_data = {'contrato': contrato, 'cliente_contratante': cliente_contratante}

        form = ContratoAssinadoForm(data=form_data)

        if form.is_valid():
            form.save()
            return redirect('contratos_disponiveis')
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
