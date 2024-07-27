from scope_auth.util import get_scope_from_request
from django.contrib.auth.context_processors import auth

from contextlib import suppress

from .models import UsuarioGenericoPessoa, PessoaFisica


def current_scope(request):
    return {'scope': get_scope_from_request(request)}


def auth_pessoa(request):
    context = auth(request)
    context['tipo_pessoa'] = None

    with suppress(TypeError):
        context['user'] = UsuarioGenericoPessoa.from_usuario(context['user'])

    context['tipo_pessoa'] = (
        'pessoa_fisica'
        if PessoaFisica.is_pessoa_fisica(context['user'])
        else 'pessoa_juridica'
    )

    return context
