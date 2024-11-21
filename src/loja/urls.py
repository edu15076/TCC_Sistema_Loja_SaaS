from django.urls import path

from .views import *

urlpatterns = [
    path(
        'loja/<int:scope>/',
        HomeLojaView.as_view(),
        name='home_loja'
    ),
    path(
        'loja/<int:scope>/criar_usuario/',
        CreateUsuarioLojaView.as_view(),
        name='criar_usuario_loja',
    ),
    path(
        'loja/<int:scope>/login/',
        LoginUsuarioLojaView.as_view(),
        name='login_loja'
    ),
    path(
        'loja/<int:scope>/editar_usuario/',
        UpdateUsuarioLojaView.as_view(),
        name='editar_usuario_loja',
    ),
    path(
        'loja/<int:scope>/logout/',
        LogoutUsuarioLojaView.as_view(),
        name='logout_loja'
    ),
    path(
        'loja/<int:scope>/editar_senha/',
        PasswordChangeUsuarioLojaView.as_view(),
        name='editar_senha_loja',
    ),
]
