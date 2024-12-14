import json

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import reverse_lazy, reverse
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views import View
from django.conf import settings

from util.mixins import MultipleFormsViewMixin
from util.views import CreateOrUpdateListHTMXView
from common.views.mixins import UsuarioMixin, UserInScopeRequiredMixin
from saas.models import Cartao, ClienteContratante
from common.models import Endereco, Periodo
from saas.forms import CartaoForm, CartaoPadraoForm

class MetodosPagamentoCRDView(
    MultipleFormsViewMixin,
    UserInScopeRequiredMixin,
    PermissionRequiredMixin,
    CreateOrUpdateListHTMXView
):
    model = Cartao
    form_class = CartaoForm
    forms_class = {
        'cartao_padrao': CartaoPadraoForm,
        'cartao': CartaoForm,
    }
    template_name = 'metodos_pagamento/metodos_pagamento.html'
    login_url = reverse_lazy('login_contratacao')

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_metodos_de_pagamento'

    def get_context_data(self, **kwargs):
        context = {}

        forms = self.get_forms()
        for form in forms.values():
            context[form.form_name()] = form

        cartao_padrao = Cartao.cartoes.filter(cliente_contratante=self.user, padrao=True).first()
        context['cartao_padrao'] = cartao_padrao
        context['cartoes'] = Cartao.cartoes.filter(cliente_contratante=self.user)
        if cartao_padrao is not None:
            context['cartoes'] = context['cartoes'].exclude(pk=cartao_padrao.pk)
        context['cartoes_count'] = Cartao.cartoes.filter(cliente_contratante=self.user).count()
        context['bandeiras'] = Cartao.Bandeiras
        context['public_key'] = settings.STRIPE_PUBLIC_KEY

        return context
    
    def get_template_names(self):
        template_name = self.template_name


        request = self.request
        if request is not None:
            if self.forms_class['cartao_padrao'].submit_name() in request.POST or self.user.cartoes.count() == 1:
                template_name = 'metodos_pagamento/metodos_pagamento_conteudo.html'
            else:
                template_name = 'metodos_pagamento/cards/card_metodo_pagamento.html'

        return [template_name]
    
    def get_form_kwargs(self, form_class=None, request=None):
        kwargs = super().get_form_kwargs()

        if request is not None:
            if self.forms_class['cartao_padrao'].submit_name() in request.POST:
                kwargs['data'] = request.POST
            elif self.forms_class['cartao'].submit_name() in json.loads(request.body):
                kwargs['data'] = json.loads(request.body)

        kwargs['user'] = self.user

        return kwargs

    def get_form(self, form_class=None, form_name = None, request = None):
        if form_class is not None or form_name is not None:
            return super().get_form(form_class, form_name, request)
        elif self.forms_class['cartao_padrao'].submit_name() in request.POST:
            return super().get_form(form_class=self.forms_class['cartao_padrao'])
        else:
            return super().get_form(form_class=self.forms_class['cartao'], request=request)

    def form_valid(self, form):
        cartao = form.save()
        context = {}

        if type(form) == self.forms_class['cartao_padrao']:
            context = self.get_context_data()
        elif self.user.cartoes.count() == 1:
            context = self.get_context_data()
        else: 
            context['cartao'] = cartao
            context['bandeiras'] = Cartao.Bandeiras
        context['erros'] = form.errors

        return render(
            self.request, 
            self.get_template_names(), 
            context
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        return render(request, self.template_name, self.get_context_data())
