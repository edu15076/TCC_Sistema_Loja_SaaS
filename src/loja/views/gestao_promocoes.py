from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from util.mixins import MultipleFormsViewMixin
from loja.models.funcionario import GerenteFinanceiro
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Promocao
from loja.views import UserFromLojaRequiredMixin, FilterForSameLojaMixin
from loja.forms import DuplicarPromocaoForm, PromocaoForm, FiltroPromocaoForm

# TODO - Passar loja no get_form_kwargs


class GestaoPromocoesCRUDListView(
    MultipleFormsViewMixin,
    UserFromLojaRequiredMixin,
    FilterForSameLojaMixin,
    PermissionRequiredMixin,
    CreateOrUpdateListHTMXView,
):
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True
    template_name = 'promocoes.html'
    filter_form = FiltroPromocaoForm
    model = Promocao
    object = None
    default_order = ['id']
    paginate_by = 30
    usuario_class = GerenteFinanceiro
    forms_class = {
        'promocao': PromocaoForm,
        'duplicar_promocao': DuplicarPromocaoForm,
    }

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = {}

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        context['promocoes'] = self.object_list
        context['filter_form'] = self.filter_form(scope=self.scope)
        context['promocoes_count'] = Promocao.promocoes.filter(
            loja__scope=self.scope
        ).count()

        return context

    def get_form_kwargs(self, form_class=None, request=None) -> dict[str, any]:
        kwargs = super().get_form_kwargs()
        kwargs['scope'] = self.scope
        kwargs['instance'] = self.get_object()

        return kwargs

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())

    def get_template_names(self) -> list[str]:
        templates = [self.template_name]

        request = self.request
        cards = request.GET.get('visualizacao') == 'cards'

        if cards:
            templates.append('cards/card_promocao.html')
        else:
            templates.append('linhas/linha_promocao.html')

        return templates

    def form_valid(self, form):
        promocao = form.save()
        erros = form.errors

        return render(
            self.request,
            self.get_template_names()[1],
            {'promocao': promocao, 'erros': erros},
        )

    # TODO def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
