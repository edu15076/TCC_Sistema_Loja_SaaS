from django.urls import path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    path(
        'loja/criar_usuario/',
        CreateUsuarioLojaView.as_view(),
        name='criar_usuario_loja',
    ),
    path('loja/login/', LoginUsuarioLojaView.as_view(), name='login_loja'),
    path(
        'loja/', TemplateView.as_view(template_name='base_loja.html'), name='home_loja'
    ),
    path(
        'loja/editar_usuario/',
        UpdateUsuarioLojaView.as_view(),
        name='editar_usuario_loja',
    ),
    path('loja/logout/', LogoutUsuarioLojaView.as_view(), name='logout_loja'),
    path(
        'loja/editar_senha/',
        PasswordChangeUsuarioLojaView.as_view(),
        name='editar_senha_loja',
    ),
]
