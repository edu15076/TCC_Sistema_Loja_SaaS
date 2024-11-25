from django.urls import path

from .views import *

urlpatterns = [
    path(
        '',
        HomeLojaView.as_view(),
        name='home_loja'
    ),
    path(
        'criar_usuario/',
        CreateUsuarioLojaView.as_view(),
        name='criar_usuario_loja',
    ),
    path(
        'login/',
        LoginUsuarioLojaView.as_view(),
        name='login_loja'
    ),
    path(
        'editar_usuario/',
        UpdateUsuarioLojaView.as_view(),
        name='editar_usuario_loja',
    ),
    path(
        'logout/',
        LogoutUsuarioLojaView.as_view(),
        name='logout_loja'
    ),
    path(
        'editar_senha/',
        PasswordChangeUsuarioLojaView.as_view(),
        name='editar_senha_loja',
    ),
    path(
        'loja/<int:scope>/oferta_produtos/',
        GestaoOfertaProdutoListView.as_view(),
        name='gestao_oferta_produtos',
    ),
    path(
        'loja/<int:scope>/promocoes_produto/<int:pk>/',
        GestaoPromocoesProdutoCRUDView.as_view(),
        name='gestao_promocoes_produto',
    ),
]
