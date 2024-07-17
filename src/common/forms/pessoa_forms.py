from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from ..models import Pessoa, PessoaFisica, PessoaJuridica
from ..validators import codigo_validator, PESSOA_FISICA_CODIGO_LEN, \
    PESSOA_JURIDICA_CODIGO_LEN


class PessoaCreationForm(forms.ModelForm):
    error_messages = {
        'codigo_invalido': _('O código é inválido'),
        'scope_dne': _('O escpo passado não existe'),
    }

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
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
        abstract = True
        fields = ('codigo',)


class PessoaFisicaCreationForm(PessoaCreationForm):
    error_messages = {
        'cpf_invalido': _('O CPF é inválido'),
        'codigo_invalido': _('O código é inválido'),
    } | PessoaCreationForm.error_messages

    def clean_codigo(self):
        codigo = super().clean_codigo()
        if (codigo and isinstance(codigo, str) and
                len(codigo) != PESSOA_FISICA_CODIGO_LEN):
            raise ValidationError(
                self.error_messages['cpf_invalido'],
                code='cpf_invalido',
            )
        return codigo

    class Meta:
        model = PessoaFisica
        abstract = True
        fields = ('codigo', 'nome', 'sobrenome', 'data_nascimento')


class PessoaJuridicaCreationForm(PessoaCreationForm):
    error_messages = {
        'cnpj_invalido': _('O CNPJ é inválido'),
        'codigo_invalido': _('O código é inválido'),
    } | PessoaCreationForm.error_messages

    def clean_codigo(self):
        codigo = super().clean_codigo()
        if (codigo and isinstance(codigo, str) and
                len(codigo) != PESSOA_JURIDICA_CODIGO_LEN):
            raise ValidationError(
                self.error_messages['cnpj_invalido'],
                code='cnpj_invalido',
            )
        return codigo

    class Meta:
        model = PessoaJuridica
        abstract = True
        fields = ('codigo', 'razao_social', 'nome_fantasia')
