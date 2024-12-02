from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from loja.models.funcionario import GerenteFinanceiro
from util.views.edit_list import CreateOrUpdateListHTMXView
from loja.models import Promocao
from loja.views import UserFromLojaRequiredMixin
from loja.forms import DuplicarPromocaoForm, PromocaoForm, FiltroPromocaoForm


class GestaoPromocoesCRUDListView(
    UserFromLojaRequiredMixin, PermissionRequiredMixin, CreateOrUpdateListHTMXView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'promocoes.html'
    duplicar_promocao_form_class = DuplicarPromocaoForm
    form_class = PromocaoForm
    filter_form = FiltroPromocaoForm
    model = Promocao
    object = None
    default_order = ['id']
    paginate_by = 30
    usuario_class = GerenteFinanceiro
    permission_required = 'loja.gerir_oferta_de_produto'
    raise_exception = True

    def get_form(self, form_class: type | None = ...):
        return self.form_class(scope=self.scope)

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)

        # context = {}
        context['promocoes'] = self.object_list
        context['duplicar_form'] = self.duplicar_promocao_form_class(scope=self.scope)
        context['form'] = self.get_form()
        context['filter_form'] = self.filter_form(scope=self.scope)
        context['promocoes_count'] = Promocao.promocoes.filter(
            loja__scope=self.scope
        ).count()

        return context

    def get_form_kwargs(self):
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

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        try:
            if 'promocao' not in request.POST:
                form = self.form_class(data=request.POST, scope=self.scope)
            else:
                form = self.duplicar_promocao_form_class(
                    data=request.POST, scope=self.scope
                )

            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
