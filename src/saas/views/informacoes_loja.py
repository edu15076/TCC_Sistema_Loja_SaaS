from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseNotFound, JsonResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from common.views.mixins import UserInScopeRequiredMixin
from loja.models import Loja, Admin, Funcionario, funcionario
from loja.views import FilterForSameLojaMixin
from loja.views.abstract import (
    FuncionarioContextDataMixin,
    ABCListFuncionariosView,
    ABCCardFuncionarioView,
    ABCCriarFuncionarioView,
    ABCTrocarFuncionarioIsValidView,
    ABCDesativarFuncionarioView,
    ABCReativarFuncionarioView,
    ABCTrocarPapelFuncionarioView,
    ABCAdicionarPapelFuncionarioView,
    ABCRemoverPapelFuncionarioView
)
from util.views import UpdateHTMXView, HTMXTemplateView, HTMXFormMixin
from ..forms import LojaForm
from ..forms.informacoes_loja_forms import (
    AdminCreationForm,
    FuncionarioIsAdminForm
)
from ..models import ClienteContratante

__all__ = (
    'EditarDadosLojaView',
    'DadosLojaView',
    'AdminContextDataMixin',
    'ListAdminsView',
    'CardAdminView',
    'CriarAdminView',
    'TrocarAdminIsValidView',
    'DesativarAdminView',
    'ReativarAdminView',
    'TrocarPapelFuncionarioView',
    'AdicionarPapelFuncionarioView',
    'RemoverPapelFuncionarioView',
    'TrocarIsAdminFuncionarioView',
    'InformacoesLojaView',
)


class EditarDadosLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, UpdateHTMXView
):
    model = Loja
    form_class = LojaForm
    template_name = 'informacoes_loja/gestao_loja/modals/modal_editar_dados_loja.html'
    form_template_name = 'informacoes_loja/gestao_loja/forms/htmx_edit_loja.html'
    usuario_class = ClienteContratante
    form_action = reverse_lazy('editar_dados_loja')
    success_url = reverse_lazy('dados_loja')
    redirect_on_success = False
    restrict_direct_access = True
    login_url = reverse_lazy('login_contratacao')
    permission_required = 'saas.gerir_cadastro_da_loja'
    hx_target_form_invalid = 'this'
    hx_swap_form_invalid = 'outerHTML'

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'auto_id': 'id_edit_loja_%s'}

    def get_object(self, queryset=None):
        return self.user.loja


class DadosLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, HTMXTemplateView
):
    template_name = 'informacoes_loja/gestao_loja/cards/card_dados_loja.html'
    restrict_direct_access = True
    login_url = reverse_lazy('login_contratacao')
    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_cadastro_da_loja'

    @property
    def extra_context(self):
        return {**(super().extra_context or {}), 'loja': self.user.loja}


class AdminContextDataMixin(FuncionarioContextDataMixin):
    def get_context_data_funcionario(self, funcionario: Funcionario):
        funcionario = super().get_context_data_funcionario(funcionario)
        funcionario.is_admin_change_form = FuncionarioIsAdminForm(
            initial={
                'funcionario': funcionario.pk,
                'is_admin': funcionario.is_admin,
            },
            loja=self.user.loja,
            auto_id=f'change-is-admin-funcionario-{funcionario.pk}-%s'
        )
        return funcionario


class ListAdminsView(
    UserInScopeRequiredMixin,
    FilterForSameLojaMixin,
    PermissionRequiredMixin,
    AdminContextDataMixin,
    ABCListFuncionariosView
):
    template_name = 'informacoes_loja/gestao_admins/includes/list_admins.html'
    login_url = reverse_lazy('login_contratacao')
    ordering = ['-is_active', '-is_admin', 'nome']
    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'


class CardAdminView(
    UserInScopeRequiredMixin,
    FilterForSameLojaMixin,
    AdminContextDataMixin,
    ABCCardFuncionarioView
):
    template_name = 'informacoes_loja/gestao_admins/cards/card_admin.html'
    login_url = reverse_lazy('login_contratacao')

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'


class CriarAdminView(
    UserInScopeRequiredMixin,
    PermissionRequiredMixin,
    ABCCriarFuncionarioView
):
    model = Admin
    form_class = AdminCreationForm
    template_name = 'informacoes_loja/gestao_admins/modals/modal_criar_admin.html'
    form_action = reverse_lazy('criar_admin')
    login_url = reverse_lazy('login_contratacao')

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'

    def get_success_url(self):
        return reverse('admin_detail', kwargs={'pk': self.object.pk})


class TrocarAdminIsValidView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, ABCTrocarFuncionarioIsValidView
):
    login_url = reverse_lazy('login_contratacao')

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'

    def get_success_url(self):
        return reverse('admin_detail', kwargs=self.get_success_url_kwargs())


class DesativarAdminView(TrocarAdminIsValidView, ABCDesativarFuncionarioView):
    pass


class ReativarAdminView(TrocarAdminIsValidView, ABCReativarFuncionarioView):
    pass


class TrocarPapelFuncionarioView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, ABCTrocarPapelFuncionarioView
):
    login_url = reverse_lazy('login_contratacao')

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'


class AdicionarPapelFuncionarioView(
    TrocarPapelFuncionarioView, ABCAdicionarPapelFuncionarioView
):
    form_action: str = reverse_lazy('adicionar_papel')

    def get_success_url(self):
        return reverse('remover_papel', kwargs=self.get_success_url_kwargs())


class RemoverPapelFuncionarioView(
    TrocarPapelFuncionarioView, ABCRemoverPapelFuncionarioView
):
    form_action: str = reverse_lazy('remover_papel')

    def get_success_url(self):
        return reverse('adicionar_papel', kwargs=self.get_success_url_kwargs())


class TrocarIsAdminFuncionarioView(
    UserInScopeRequiredMixin,
    FilterForSameLojaMixin,
    PermissionRequiredMixin,
    HTMXFormMixin,
    FormView
):
    form_class = FuncionarioIsAdminForm
    login_url = reverse_lazy('login_contratacao')
    redirect_on_success = False
    success_url = None

    usuario_class = ClienteContratante
    permission_required = 'saas.gerir_admins_da_loja'

    def get(self, *args, **kwargs):
        return HttpResponseNotFound()

    def get_success_url(self):
        return reverse('admin_detail', kwargs=self.get_success_url_kwargs())

    def get_success_url_kwargs(self) -> dict:
        return {
            'pk': self.form.cleaned_data['funcionario'].pk,
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'loja': self.user.loja}

    def get_form(self, form_class=None):
        if not hasattr(self, 'form'):
            setattr(self, 'form', super().get_form(form_class))
        return self.form

    def form_invalid(self, form):
        # TODO: posteriormente alterar isso para mostrar um erro
        return JsonResponse({'status': True}, status=422)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class InformacoesLojaView(
    UserInScopeRequiredMixin, PermissionRequiredMixin, TemplateView
):
    template_name = 'informacoes_loja/informacoes_loja.html'
    usuario_class = ClienteContratante
    login_url = reverse_lazy('login_contratacao')
    permission_required = [
        'saas.gerir_cadastro_da_loja', 'saas.gerir_admins_da_loja'
    ]

    @property
    def extra_context(self):
        return {**(super().extra_context or {}), 'loja': self.user.loja}
