from contextlib import suppress

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import Group
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView
from django.views.generic.edit import FormView

from common.views import CreateUsuarioGenericoView
from common.views.mixins import UserInScopeRequiredMixin
from loja.models import Loja, Admin, Funcionario, GerenteDeRH
from loja.views import FilterForSameLojaMixin
from util.views import UpdateHTMXView, HTMXTemplateView, CreateHTMXView, \
    CreateOrUpdateListHTMXView, HTMXHelperMixin, HTMXModelFormMixin, HTMXFormMixin
from ..forms import LojaForm
from ..forms.informacoes_loja_forms import AdminCreationForm, FuncionarioGroupForm, \
    IsAdminForm, IsActiveFuncionarioForm
from ..models import ClienteContratante

__all__ = (
    'ChangeIsAdmin',
    'DadosLojaView',
    'EditarDadosLojaView',
    'InformacoesLojaView',
    'CriarAdminLojaView',
    'ListAdminView',
    'AddFuncionarioGroupView',
    'RemoveFuncionarioGroupView',
    'AdminCardView',
    'ReativarUsuario',
    'DesativarFuncionarioView',
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

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'auto_id': 'id_edit_loja_%s'}

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

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {'auto_id': 'id_create_admin_%s'}

    def get_success_url(self):
        return reverse('admin_detail', kwargs={'pk': self.object.pk})

    def get_created_user_scope(self):
        return self.user.loja.scope


class ChangeFuncionarioIsValidView(
    UserInScopeRequiredMixin, HTMXFormMixin, FormView
):
    form_class = IsActiveFuncionarioForm
    login_url = reverse_lazy('login_contratacao')
    redirect_on_success = False
    success_url = None
    is_active_next = False
    usuario_class = ClienteContratante

    def get(self, *args, **kwargs):
        return HttpResponseNotFound()

    def get_success_url(self):
        return reverse('admin_detail', kwargs=self.get_success_url_kwargs())

    def get_success_url_kwargs(self) -> dict:
        return {
            'pk': self.form.cleaned_data['funcionario'].pk,
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'is_active_next': self.is_active_next,
        }

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


class DesativarFuncionarioView(
    ChangeFuncionarioIsValidView
):
    is_active_next = False


class ReativarUsuario(
    ChangeFuncionarioIsValidView
):
    is_active_next = True


class BaseFuncionarioPapeisMixin(
    UserInScopeRequiredMixin, FilterForSameLojaMixin, PermissionRequiredMixin
):
    usuario_class = [ClienteContratante, GerenteDeRH]
    permission_required = 'saas.gerir_conta_de_admin_da_loja'

    # TODO: alterar para permissão da loja

    def _get_papeis(self, funcionario: Funcionario, action: bool, groups):
        return [
            group | {
                'form': FuncionarioGroupForm(
                    initial={
                        'group': group['pk'],
                        'funcionario': funcionario.pk,
                        'action': action,
                    },
                    loja=self.user.loja,
                    auto_id=f'change-funcionario-papel-'
                            f'{funcionario.pk}-group-{group['pk']}-%s'
                )
            } for group in groups.values('name', 'pk')
        ]

    def get_papeis_pertence(self, funcionario: Funcionario):
        return self._get_papeis(funcionario, False, funcionario.groups.all())

    def get_papeis_nao_pertence(self, funcionario: Funcionario):
        return self._get_papeis(funcionario, True, funcionario.not_in_groups())

    def get_context_data_funcionario(self, funcionario: Funcionario):
        funcionario.papeis_pertence = self.get_papeis_pertence(funcionario)
        funcionario.papeis_nao_pertence = self.get_papeis_nao_pertence(funcionario)
        funcionario.is_admin_change_form = IsAdminForm(
            initial={
                'funcionario': funcionario.pk,
                'is_admin': funcionario.is_admin,
            },
            loja=self.user.loja,
            auto_id=f'change-is-admin-funcionario-{funcionario.pk}-%s'
        )
        funcionario.is_active_change_form = IsActiveFuncionarioForm(
            initial={
                'funcionario': funcionario.pk,
                'is_active': not funcionario.is_active,
            },
            loja=self.user.loja,
            auto_id=f'change-is-active-funcionario-{funcionario.pk}-%s'
        )
        return funcionario


class ChangeIsAdmin(
    UserInScopeRequiredMixin, FilterForSameLojaMixin, HTMXFormMixin, FormView
):
    form_class = IsAdminForm
    login_url = reverse_lazy('login_contratacao')
    redirect_on_success = False
    success_url = None
    usuario_class = ClienteContratante

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


class AdminCardView(
    BaseFuncionarioPapeisMixin, HTMXHelperMixin, DetailView
):
    template_name = 'cards/card_admin_loja.html'
    restrict_direct_access = True
    model = Funcionario
    usuario_class = ClienteContratante
    context_object_name = 'funcionario'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.get_context_data_funcionario(context['funcionario'])
        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups')


class ListAdminView(
    BaseFuncionarioPapeisMixin, HTMXHelperMixin, ListView
):
    login_url = reverse_lazy('login_contratacao')
    template_name = 'includes/admin_list.html'
    model = Funcionario
    # TODO: fix pagination paginate_by = 20
    restrict_direct_access = False
    usuario_class = ClienteContratante
    ordering = ['-is_active', '-is_admin', 'nome']
    context_object_name = 'funcionarios'
    permission_required = 'saas.gerir_conta_de_admin_da_loja'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        for funcionario in context['funcionarios']:
            self.get_context_data_funcionario(funcionario)

        return context

    def get_queryset(self):
        return super().get_queryset().prefetch_related('groups')


class ChangeFuncionarioGroupView(
    UserInScopeRequiredMixin, HTMXFormMixin, FormView
):
    form_class = FuncionarioGroupForm
    login_url = reverse_lazy('login_contratacao')
    action = True
    redirect_on_success = False
    success_url = None
    usuario_class = ClienteContratante

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)
        with suppress(Group.DoesNotExist):
            context_data['group'] = Group.objects.get(pk=self.kwargs.get('group'))
        context_data['funcionario_pk'] = str(self.kwargs.get('funcionario'))
        return context_data

    def get_initial(self):
        return {
            'group': self.kwargs.get('group'),
            'funcionario': self.kwargs.get('funcionario'),
        }

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {
            'loja': self.user.loja,
            'action': self.action,
        }

    def get_success_url_kwargs(self) -> dict:
        return {
            'group': self.form.cleaned_data['group'].pk,
            'funcionario': self.form.cleaned_data['funcionario'].pk,
        }

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


class AddFuncionarioGroupView(ChangeFuncionarioGroupView):
    template_name = 'pills/pill_adicionar_papel.html'
    action = True

    def get_success_url(self):
        return reverse('remove_papel', kwargs=self.get_success_url_kwargs())


class RemoveFuncionarioGroupView(ChangeFuncionarioGroupView):
    template_name = 'pills/pill_remover_papel.html'
    action = False

    def get_success_url(self):
        return reverse('add_papel', kwargs=self.get_success_url_kwargs())


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
