from crispy_forms.layout import Submit

from django.db import transaction
from django.contrib.auth.forms import (
    BaseUserCreationForm,
    AuthenticationForm,
    UserChangeForm,
)
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

from scope_auth.models import Scope
from util.forms import CrispyFormMixin
from .pessoa_forms import (
    PessoaCreationForm,
    PessoaFisicaCreationForm,
    PessoaJuridicaCreationForm,
    PessoaChangeForm,
    PessoaFisicaChangeForm,
    PessoaJuridicaChangeForm,
)
from ..models import (
    UsuarioGenerico,
    PessoaUsuario,
    UsuarioGenericoPessoaFisica,
    UsuarioGenericoPessoaJuridica,
)
from ..validators import PESSOA_FISICA_CODIGO_LEN, PESSOA_JURIDICA_CODIGO_LEN


__all__ = (
    'UsuarioGenericoCreationForm',
    'UsuarioGenericoPessoaFisicaCreationForm',
    'UsuarioGenericoPessoaJuridicaCreationForm',
    'UsuarioGenericoAuthenticationForm',
    'UsuarioGenericoPessoaFisicaAuthenticationForm',
    'UsuarioGenericoPessoaJuridicaAuthenticationForm',
    'UsuarioGenericoChangeForm',
    'UsuarioGenericoPessoaFisicaChangeForm',
    'UsuarioGenericoPessoaJuridicaChangeForm',
)


class UsuarioGenericoCreationForm(
    CrispyFormMixin, BaseUserCreationForm, PessoaCreationForm
):
    error_messages = (
        BaseUserCreationForm.error_messages
        | PessoaCreationForm.error_messages
        | {
            'usuario_pre_existente': _(
                'O usuário com esse código já está ' 'cadastrado'
            ),
        }
    )

    def __init__(self, *args, scope: Scope, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()
        self.scope = scope

    def get_submit_button(self):
        return Submit('criar', 'Criar')

    def clean_codigo(self):
        codigo = super().clean_codigo()
        if not codigo:
            return codigo
        try:
            PessoaUsuario.codigos.get_by_natural_key(
                codigo_pessoa=codigo, scope=self.scope
            )
        except PessoaUsuario.DoesNotExist:
            return codigo
        else:
            raise ValidationError(
                self.error_messages['usuario_pre_existente'],
                code='usuario_pre_existente',
            )

    def _save_pessoa_usuario(self, instance):
        pessoa_usuario = PessoaUsuario.codigos.get_or_create_by_natural_key(
            codigo_pessoa=instance.codigo, scope=self.scope
        )
        instance.pessoa_usuario = pessoa_usuario

    @transaction.atomic
    def save(self, commit=True):
        user: UsuarioGenerico = super().save(commit=False)

        if commit:
            self._save_pessoa_usuario(user)
            user.save()
            if hasattr(self, 'save_m2m'):
                self.save_m2m()
        return user

    class Meta:
        model = UsuarioGenerico
        fields = PessoaCreationForm.Meta.fields


class UsuarioGenericoPessoaFisicaCreationForm(
    UsuarioGenericoCreationForm, PessoaFisicaCreationForm
):
    error_messages = (
        UsuarioGenericoCreationForm.error_messages
        | PessoaFisicaCreationForm.error_messages
    )

    class Meta:
        model = UsuarioGenericoPessoaFisica
        fields = PessoaFisicaCreationForm.Meta.fields
        labels = getattr(PessoaFisicaCreationForm.Meta, 'labels', {})


class UsuarioGenericoPessoaJuridicaCreationForm(
    UsuarioGenericoCreationForm, PessoaJuridicaCreationForm
):
    error_messages = (
        UsuarioGenericoCreationForm.error_messages
        | PessoaJuridicaCreationForm.error_messages
    )

    class Meta:
        model = UsuarioGenericoPessoaJuridica
        fields = PessoaJuridicaCreationForm.Meta.fields
        labels = getattr(PessoaJuridicaCreationForm.Meta, 'labels', {})


class UsuarioGenericoAuthenticationForm(CrispyFormMixin, AuthenticationForm):
    error_messages = AuthenticationForm.error_messages | {
        'tipo_usuario_invalido': _('O tipo do usuário é inválido')
    }
    username_length = None
    username_label = 'Código'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = self.username_label
        self.helper = self.create_helper()

    def get_submit_button(self) -> Submit:
        return Submit('login', 'Login')

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if len(username) != self.username_length:
                raise ValidationError(
                    self.error_messages['tipo_usuario_invalido'],
                    code='tipo_usuario_invalido',
                )

        return username


class UsuarioGenericoPessoaFisicaAuthenticationForm(UsuarioGenericoAuthenticationForm):
    error_messages = UsuarioGenericoAuthenticationForm.error_messages | {
        'tipo_usuario_invalido': _('O tipo do usuário deve ser um CPF')
    }
    username_length = PESSOA_FISICA_CODIGO_LEN
    username_label = 'CPF'

    class Meta:
        model = UsuarioGenericoPessoaFisica


class UsuarioGenericoPessoaJuridicaAuthenticationForm(
    UsuarioGenericoAuthenticationForm
):
    error_messages = UsuarioGenericoAuthenticationForm.error_messages | {
        'tipo_usuario_invalido': _('O tipo do usuário deve ser um CNPJ')
    }
    username_length = PESSOA_JURIDICA_CODIGO_LEN
    username_label = 'CNPJ'

    class Meta:
        model = UsuarioGenericoPessoaJuridica


class UsuarioGenericoChangeForm(CrispyFormMixin, UserChangeForm, PessoaChangeForm):
    password = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = self.create_helper()

    def get_submit_button(self):
        return Submit('alterar', 'Alterar')

    class Meta:
        model = UsuarioGenerico
        fields = PessoaChangeForm.Meta.fields


class UsuarioGenericoPessoaFisicaChangeForm(
    UsuarioGenericoChangeForm, PessoaFisicaChangeForm
):
    class Meta:
        model = UsuarioGenericoPessoaFisica
        fields = (
            UsuarioGenericoChangeForm.Meta.fields + PessoaFisicaChangeForm.Meta.fields
        )


class UsuarioGenericoPessoaJuridicaChangeForm(
    UsuarioGenericoChangeForm, PessoaJuridicaChangeForm
):
    class Meta:
        model = UsuarioGenericoPessoaJuridica
        fields = (
            UsuarioGenericoChangeForm.Meta.fields + PessoaJuridicaChangeForm.Meta.fields
        )
