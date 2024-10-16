from django.utils.deconstruct import deconstructible
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from util.logging import Loggers


__all__ = (
    'cpf_validator',
    'cnpj_validator',
    'codigo_validator',
    'PESSOA_FISICA_CODIGO_LEN',
    'PESSOA_JURIDICA_CODIGO_LEN'
)


PESSOA_FISICA_CODIGO_LEN = 11
PESSOA_JURIDICA_CODIGO_LEN = 14

def cpf_validator(cpf: str) -> None:
    # Check if the value is empty or has fewer than 11 digits
    if not cpf or len(cpf) != 11:
        raise ValidationError(_('CPF inválido'))

    if not cpf.isdigit():
        raise ValidationError(_('CPF deve ser numérico'))

    # Calculate the first check digit
    sum = 0
    for i in range(9):
        sum += int(cpf[i]) * (i + 1)
    check_digit1 = sum % 11
    if check_digit1 == 10:
        check_digit1 = 0

    # Check if the first check digit is correct
    if check_digit1 != int(cpf[9]):
        raise ValidationError(_('CPF inválido'))

    # Calculate the second check digit
    sum = 0
    for i in range(10):
        sum += int(cpf[i]) * i
    check_digit2 = sum % 11
    if check_digit2 == 10:
        check_digit2 = 0

    # Check if the second check digit is correct
    if check_digit2 != int(cpf[10]):
        raise ValidationError(_('CPF inválido'))


def cnpj_validator(cnpj: str) -> None:
    # Verifica se o CNPJ tem 14 dígitos
    if not cnpj or len(cnpj) != 14:
        raise ValidationError(_('CNPJ inválido'))

    if not cnpj.isdigit():
        raise ValidationError(_('CNPJ deve ser numérico'))

    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula o primeiro dígito verificador
    soma = 0
    for digito, peso in zip(cnpj, pesos):
        soma += int(digito) * peso

    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(cnpj[12]) != digito1:
        raise ValidationError(_('CNPJ inválido'))

    pesos.insert(0, 6)

    # Calcula o segundo dígito verificador
    soma = 0
    for digito, peso in zip(cnpj, pesos):
        soma += int(digito) * peso

    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(cnpj[13]) != digito2:
        raise ValidationError(_('CNPJ inválido'))


def codigo_validator(codigo: str) -> None:
    if len(codigo) == 11:
        cpf_validator(codigo)
    else:
        cnpj_validator(codigo)


@deconstructible
class CEPValidator:
    def __init__(self, get_providers_func):
        self.get_providers = get_providers_func

    def __call__(self, value):
        if not value or len(value) != 8:
            ValidationError(_('CEP inválido'))

        logger = Loggers.get_logger()

        providers = self.get_providers()
        for provider in providers:
            try:
                cep_data = provider.get_cep_data(value)

                if cep_data is not None:
                    return
            except Exception as e:
                logger.warning(_((
                    f"{e.args[0]} na solicitação ao provedor "
                    f"{provider.provider_id}"
                )))

        raise ValidationError(_(f"CEP não existe"))