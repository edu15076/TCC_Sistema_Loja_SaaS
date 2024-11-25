from typing import Any

from django.db.models.query import QuerySet
from django.views.generic.detail import DetailView
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import render

from common.models.scopes import LojaScope
from util.views.edit_list import CreateOrUpdateListHTMXView
from util.views.htmx import UpdateHTMXView
from common.views.mixins import UsuarioMixin
from loja.models import Produto, Promocao
from common.models import Periodo
from loja.forms import (
    DuplicarPromocaoForm,
    PromocaoForm,
    FiltroPromocaoForm
)

class GestaoPromocoesCRUDListView(
    # LoginRequiredMixin, UsuarioMixin, CreateOrUpdateListHTMXView
    CreateOrUpdateListHTMXView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'promocoes.html'
    duplicar_promocao_form_class = DuplicarPromocaoForm
    form_class = PromocaoForm
    filter_form = FiltroPromocaoForm
    model = Promocao
    object_pk = None
    object = None
    default_order = ['id']
    paginate_by = 30

    # todo remover isso e adicionar FuncionarioFromLojaRequiredMixin
    scope = 2

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        self.object_list.filter(loja__scope=self.scope)
        
        context = {}
        context['promocoes'] = self.object_list
        # context['form'] = self.form_class()
        context['dupliar_form'] = self.duplicar_promocao_form_class()
        context['form'] = self.form_class()
        context['filter_form'] = self.filter_form(self.scope)
        context['promocoes_count'] = Promocao.promocoes.filter(loja__scope=self.scope).count()

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        # return super().post(request, *args, **kwargs)
        try:
            promocao = self.get_object()

            if promocao is None:
                form = self.form_class(request.POST)
            else:
                form = self.duplicar_promocao_form_class(
                    data=request.POST, loja=promocao
                )

            if form.is_valid():
                self.form_valid(form)
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)