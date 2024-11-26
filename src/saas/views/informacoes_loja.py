from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView

from common.views import CreateUsuarioGenericoView
from common.views.mixins import UserInScopeRequiredMixin
from loja.models import Loja, Admin, Funcionario, GerenteDeRH
from util.views import UpdateHTMXView, HTMXTemplateView, CreateHTMXView, \
    CreateOrUpdateListHTMXView, HTMXHelperMixin, HTMXModelFormMixin
from ..forms import LojaForm
from ..forms.informacoes_loja_forms import AdminCreationForm, FuncionarioGroupForm
from ..models import ClienteContratante

__all__ = (
    'DadosLojaView',
    'EditarDadosLojaView',
    'InformacoesLojaView',
    'CriarAdminLojaView',
    'ListAdminView',
    'AdminCardView',
)

class EditarDadosLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, UpdateHTMXView
):
    model = Loja
    form_class = LojaForm
    template_name = 'modals/modal_editar_dados_loja.html'
    form_template_name = 'forms/htmx_loja_edit_form.html'
    usuario_class = ClienteContratante
    form_action = reverse_lazy('editar_dados_loja')
    success_url = reverse_lazy('dados_loja')
    redirect_on_success = False
    restrict_direct_access = True
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'saas.gerir_cadastro_da_loja'
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    def get_object(self, queryset=None):
        return self.user.loja


class DadosLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, HTMXTemplateView
):
    template_name = 'cards/card_dados_loja.html'
    restrict_direct_access = True
    login_url = reverse_lazy('login_contratacao')
    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_cadastro_da_loja'

    @property
    def extra_context(self):
        return {**(super().extra_context or {}), 'loja': self.user.loja}


class CriarAdminLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, CreateUsuarioGenericoView
):
    model = Admin
    form_class = AdminCreationForm
    template_name = 'modals/modal_criar_admin_loja.html'
    form_template_name = 'forms/htmx_create_admin_loja.html'
    usuario_class = ClienteContratante
    form_action = reverse_lazy('criar_admin')
    success_url = None
    redirect_on_success = False
    restrict_direct_access = True
    login_valid_user = False
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'saas.gerir_conta_de_admin_da_loja'
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    def get_success_url(self):
        return reverse('admin_detail', kwargs={'pk': self.object.pk})

    def get_created_user_scope(self):
        return self.user.loja.scope


class BaseFuncionarioPapeisMixin(
    UserInScopeRequiredMixin, PermissionRequiredMixin
):
    usuario_class = [ClienteContratante, GerenteDeRH]
    permission_required = 'saas.gerir_conta_de_admin_da_loja' # TODO: alterar para permissão da loja

    def get_papeis_pertence(self, funcionario: Funcionario):
        return [
            {
                'name': group.name,
                'form': FuncionarioGroupForm(initial={
                    'group': group.pk,
                    'funcionario': funcionario.pk,
                    'action': False,
                })
            } for group in funcionario.groups.all()
        ]

    def get_papeis_nao_pertence(self, funcionario: Funcionario):
        return [
            {
                'name': group.name,
                'form': FuncionarioGroupForm(initial={
                    'group': group.pk,
                    'funcionario': funcionario.pk,
                    'action': True,
                })
            } for group in funcionario.not_in_groups()
        ]


class AdminCardView(
    BaseFuncionarioPapeisMixin, HTMXHelperMixin, DetailView
):
    template_name = 'cards/card_admin_loja.html'
    restrict_direct_access = True
    model = Admin
    usuario_class = ClienteContratante
    context_object_name = 'funcionario'

    def get(self, request, *args, **kwargs):
        if self.should_block_request():
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        funcionario = context['funcionario']
        funcionario.papeis_pertence = self.get_papeis_pertence(funcionario)
        funcionario.papeis_nao_pertence = self.get_papeis_nao_pertence(funcionario)
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups')


class ListAdminView(
    BaseFuncionarioPapeisMixin, HTMXHelperMixin, ListView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'includes/admin_list.html'
    model = Admin
    paginate_by = 20
    restrict_direct_access = False
    usuario_class = ClienteContratante
    ordering = ['nome']
    context_object_name = 'funcionarios'
    permission_required = 'saas.gerir_conta_de_admin_da_loja'

    def get(self, request, *args, **kwargs):
        if self.should_block_request():
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for funcionario in context['funcionarios']:
            funcionario.papeis_pertence = self.get_papeis_pertence(funcionario)
            funcionario.papeis_nao_pertence = self.get_papeis_nao_pertence(funcionario)

        return context

    def get_queryset(self):
        print(len(super().get_queryset()))
        return super().get_queryset().prefetch_related('groups')


class InformacoesLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, TemplateView
):
    template_name = 'informacoes_loja.html'
    usuario_class = ClienteContratante
    login_url = reverse_lazy('login_contratacao')
    permission_required = [
        'saas.gerir_cadastro_da_loja', 'saas.gerir_conta_de_admin_da_loja'
    ]

    @property
    def extra_context(self):
        return {**(super().extra_context or {}), 'loja': self.user.loja}
