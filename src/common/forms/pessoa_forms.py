from crispy_forms.helper import FormHelper
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import Pessoa, PessoaFisica, PessoaJuridica
from ..validators import (
    codigo_validator,
    PESSOA_FISICA_CODIGO_LEN,
    PESSOA_JURIDICA_CODIGO_LEN,
)

__all__ = (
    'PessoaCreationForm',
    'PessoaFisicaCreationForm',
    'PessoaJuridicaCreationForm',
    'PessoaChangeForm',
    'PessoaFisicaChangeForm',
    'PessoaJuridicaChangeForm',
)


class PessoaCreationForm(forms.ModelForm):
    error_messages = {
        'codigo_invalido': _('O código é inválido'),
        'scope_dne': _('O escopo passado não existe'),
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    def clean_codigo(self):
        codigo: str = self.cleaned_data.get('codigo')
        if codigo:
            try:
                codigo_validator(codigo)
            except ValidationError:
                raise ValidationError(
                    self.error_messages['codigo_invalido'],
                    code='codigo_invalido',
                )
        return codigo

    class Meta:
        model = Pessoa
        fields = ('codigo', 'telefone', 'email')


class PessoaFisicaCreationForm(PessoaCreationForm):
    error_messages = {
        'cpf_invalido': _('O CPF é inválido'),
    } | PessoaCreationForm.error_messages

    def clean_codigo(self):
        validation_error = ValidationError(
            self.error_messages['cpf_invalido'],
            code='cpf_invalido',
        )
        try:
            codigo = super().clean_codigo()
        except ValidationError:
            raise validation_error
        if (
            codigo
            and isinstance(codigo, str)
            and len(codigo) != PESSOA_FISICA_CODIGO_LEN
        ):
            raise validation_error
        return codigo

    class Meta:
        model = PessoaFisica
        fields = tuple(dict.fromkeys(
            PessoaCreationForm.Meta.fields + (
                'nome',
                'sobrenome',
                'data_nascimento',
            )
        ))
        labels = {
            'codigo': 'CPF',
        }
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            )
        }


class PessoaJuridicaCreationForm(PessoaCreationForm):
    error_messages = {
        'cnpj_invalido': _('O CNPJ é inválido'),
    } | PessoaCreationForm.error_messages

    def clean_codigo(self):
        validation_error = ValidationError(
            self.error_messages['cnpj_invalido'],
            code='cnpj_invalido',
        )
        try:
            codigo = super().clean_codigo()
        except ValidationError:
            raise validation_error
        if (
            codigo
            and isinstance(codigo, str)
            and len(codigo) != PESSOA_JURIDICA_CODIGO_LEN
        ):
            raise validation_error
        return codigo

    class Meta:
        model = PessoaJuridica
        fields = tuple(dict.fromkeys(
            PessoaCreationForm.Meta.fields + ('razao_social', 'nome_fantasia')
        ))
        labels = {
            'codigo': 'CNPJ',
        }


class PessoaChangeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()

    class Meta:
        model = Pessoa
        fields = ('telefone', 'email')


class PessoaFisicaChangeForm(PessoaChangeForm):
    class Meta:
        model = PessoaFisica
        fields = tuple(dict.fromkeys(
            PessoaChangeForm.Meta.fields + ('nome', 'sobrenome', 'data_nascimento')
        ))
        widgets = {
            'data_nascimento': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            )
        }


class PessoaJuridicaChangeForm(PessoaChangeForm):
    class Meta:
        model = PessoaJuridica
        fields = tuple(dict.fromkeys(
            PessoaChangeForm.Meta.fields + ('razao_social', 'nome_fantasia')
        ))
