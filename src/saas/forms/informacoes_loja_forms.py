from django import forms
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from crispy_forms.layout import Submit, Layout, Field

from loja.forms import BaseFuncionarioCreationForm
from loja.forms.validators import ActiveFuncionarioValidator
from loja.forms.mixins import LojaValidatorFormMixin
from loja.models import Admin, Funcionario
from loja.models import Loja
from util.forms import ModalCrispyFormMixin, CrispyFormMixin, ModelIntegerField

__all__ = (
    'LojaForm',
    'DeletarLojaForm',
    'AdminCreationForm',
    'FuncionarioIsAdminForm',
)


class LojaForm(ModalCrispyFormMixin, forms.ModelForm):
    def get_fields(self):
        return [
            Field('nome'),
            Field('logo', template='widgets/clearable_image_input.html')
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('update_loja', _('Save Changes'))

    class Meta:
        model = Loja
        fields = ['nome', 'logo']
        widgets = {
            'logo': forms.ClearableFileInput(attrs={
                'accept': 'image/*',
                'img_url': reverse_lazy('logo_loja_contratacao'),
                'img_height': '6rem',
            })
        }


class DeletarLojaForm(CrispyFormMixin, forms.Form):
    error_messages = {
        'nome_incorreto': _('O nome não corresponde ao nome da loja'),
    }

    nome = forms.CharField(
        label=_('Nome'),
        required=True,
    )

    def __init__(self, *args, loja: Loja, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.loja = loja
        self.fields['nome'].help_text = (
                _(
                    'Digite o nome da sua loja '
                    '\"<span class="loja_nome">%(nome)s</span>\"'
                    ' para confirmar a deleção'
                )
                % {'nome': loja.nome}
        )

    def get_submit_button(self) -> Submit:
        return Submit('delete_loja', _('Delete Loja'), css_class='btn-danger')

    def clean_nome(self):
        nome = self.cleaned_data['nome']

        if not nome:
            return

        if nome != self.loja.nome:
            raise forms.ValidationError(
                self.error_messages['nome_incorreto'],
                code='nome_incorreto',
            )
        return nome

    def save(self) -> None:
        self.loja.contratante.delete_dados_loja()


class AdminCreationForm(ModalCrispyFormMixin, BaseFuncionarioCreationForm):
    error_messages = BaseFuncionarioCreationForm.error_messages

    def get_submit_button(self) -> Submit:
        return Submit('create_admin', _('Create Admin'))

    class Meta:
        model = Admin
        fields = BaseFuncionarioCreationForm.Meta.fields
        labels = getattr(BaseFuncionarioCreationForm.Meta, 'labels', {})
        widgets = getattr(BaseFuncionarioCreationForm.Meta, 'widgets', {})


class FuncionarioIsAdminForm(LojaValidatorFormMixin, CrispyFormMixin, forms.Form):
    fields_loja_check = ['funcionario']

    funcionario = ModelIntegerField(
        required=True,
        widget=forms.HiddenInput,
        model_cls=Funcionario,
        validators=[ActiveFuncionarioValidator()]
    )
    is_admin = forms.BooleanField(
        required=False,
        label=_('Admin'),
        widget=forms.CheckboxInput(attrs={
            'class': 'is-admin-checkbox-input'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper(add_submit_button=False)
        self.helper.layout = Layout(
            'funcionario',
            Field('is_admin', wrapper_class='form-switch'),
        )

    def save(self) -> bool:
        funcionario: Funcionario = self.cleaned_data['funcionario']
        is_admin: bool = self.cleaned_data['is_admin']
        funcionario.is_admin = is_admin
        if is_admin:
            Admin.grant_admin(funcionario)
        else:
            Admin.revoque_admin(funcionario)
        return is_admin
