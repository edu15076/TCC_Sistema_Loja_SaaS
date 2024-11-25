from scope_auth.util import get_scope_from_request
from django.contrib.auth.context_processors import auth

from contextlib import suppress

from .models import UsuarioGenericoPessoa, PessoaFisica, UsuarioGenericoPessoaFisica, \
    UsuarioGenericoPessoaJuridica


def current_scope(request):
    return {'scope': get_scope_from_request(request)}


def auth_pessoa(request):
    context = auth(request)
    context['tipo_pessoa'] = None

    def get_request_view_class(request):
        try:
            return request.resolver_match.func.view_class()
        except AttributeError:
            return None

    def get_user_from_request(request):
        view_class = get_request_view_class(request)
        usuario_classes = (
            [UsuarioGenericoPessoaFisica, UsuarioGenericoPessoaJuridica]
            if not view_class or not hasattr(view_class, '_usuario_classes')
            else view_class._usuario_classes
        )
        return UsuarioGenericoPessoa.cast_para_primeira_subclasse(
            usuario_classes, context['user']
        )

    with suppress(TypeError):
        context['user'] = get_user_from_request(request)

    context['tipo_pessoa'] = (
        'pessoa_fisica'
        if PessoaFisica.is_pessoa_fisica(context['user'])
        else 'pessoa_juridica'
    )

    return context
