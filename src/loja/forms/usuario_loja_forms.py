from common.forms import UsuarioGenericoPessoaFisicaCreationForm
from ..models import Funcionario

__all__ = (
    'BaseFuncionarioCreationForm',
    'FuncionarioCreationForm',
)


class BaseFuncionarioCreationForm(UsuarioGenericoPessoaFisicaCreationForm):
    error_messages = UsuarioGenericoPessoaFisicaCreationForm.error_messages

    class Meta:
        model = Funcionario
        fields = UsuarioGenericoPessoaFisicaCreationForm.Meta.fields
        labels = getattr(UsuarioGenericoPessoaFisicaCreationForm.Meta, 'labels', {})


class FuncionarioCreationForm(BaseFuncionarioCreationForm):
    error_messages = BaseFuncionarioCreationForm.error_messages

    class Meta:
        model = Funcionario
        fields = BaseFuncionarioCreationForm.Meta.fields  # TODO: Adicionar permicoes
        labels = getattr(BaseFuncionarioCreationForm.Meta, 'labels', {})
