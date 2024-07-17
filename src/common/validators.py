from django.core.exceptions import ValidationError


__all__ = (
    'cpf_validator',
    'cnpj_validator',
    'codigo_validator',
    'PESSOA_FISICA_CODIGO_LEN',
    'PESSOA_JURIDICA_CODIGO_LEN'
)


PESSOA_FISICA_CODIGO_LEN = 11
PESSOA_JURIDICA_CODIGO_LEN = 14


def cpf_validator(value):
    # Check if the value is empty or has fewer than 11 digits
    if not value or len(value) != 11:
        raise ValidationError('CPF inválido')

    # Calculate the first check digit
    sum = 0
    for i in range(9):
        sum += int(value[i]) * (i + 1)
    check_digit1 = sum % 11
    if check_digit1 == 10:
        check_digit1 = 0

    # Check if the first check digit is correct
    if check_digit1 != int(value[9]):
        raise ValidationError('CPF inválido')

    # Calculate the second check digit
    sum = 0
    for i in range(10):
        sum += int(value[i]) * i
    check_digit2 = sum % 11
    if check_digit2 == 10:
        check_digit2 = 0

    # Check if the second check digit is correct
    if check_digit2 != int(value[10]):
        raise ValidationError('CPF inválido')


def cnpj_validator(value):
    # Verifica se o CNPJ tem 14 dígitos
    if not value or len(value) != 14:
        raise ValidationError('CNPJ inválido')

    pesos = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    # Calcula o primeiro dígito verificador
    soma = 0
    for digito, peso in zip(value, pesos):
        soma += int(digito) * peso

    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    if int(value[12]) != digito1:
        raise ValidationError('CNPJ inválido')

    pesos.insert(0, 6)

    # Calcula o segundo dígito verificador
    soma = 0
    for digito, peso in zip(value, pesos):
        soma += int(digito) * peso

    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    if int(value[13]) != digito2:
        raise ValidationError('CNPJ inválido')


def codigo_validator(value):
    if len(value) == 11:
        cpf_validator(value)
    else:
        cnpj_validator(value)
