from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseNotFound
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView

from common.views import CreateUsuarioGenericoView
from common.views.mixins import UserInScopeRequiredMixin
from loja.models import Loja, Admin, Funcionario
from util.views import UpdateHTMXView, HTMXTemplateView, CreateHTMXView, \
    CreateOrUpdateListHTMXView, HTMXHelperMixin
from ..forms import LojaForm
from ..forms.informacoes_loja_forms import AdminCreationForm
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

    def get_success_url(self):
        return reverse('admin_detail', kwargs={'pk': self.object.pk})

    def get_created_user_scope(self):
        return self.user.loja.scope


class AdminCardView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, HTMXHelperMixin, DetailView
):
    template_name = 'cards/card_admin_loja.html'
    restrict_direct_access = True
    model = Admin
    usuario_class = ClienteContratante
    context_object_name = 'funcionario'
    permission_required = 'saas.gerir_conta_de_admin_da_loja'

    def get(self, request, *args, **kwargs):
        if self.should_block_request():
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)


class ListAdminView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, HTMXHelperMixin, ListView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'includes/admin_list.html'
    model = Admin
    paginate_by = 20
    restrict_direct_access = True
    usuario_class = ClienteContratante
    ordering = ['nome']
    context_object_name = 'admins'
    permission_required = 'saas.gerir_conta_de_admin_da_loja'

    def get(self, request, *args, **kwargs):
        if self.should_block_request():
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().simple()


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
