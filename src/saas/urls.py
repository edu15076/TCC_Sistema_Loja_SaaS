from django.urls import path, re_path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    path('criar_usuario/',
        CreateUsuarioContratacaoView.as_view(),
        name='criar_usuario_contratacao'),
    path('login/',
        LoginUsuarioContratacaoView.as_view(),
        name='login_contratacao'),
    path('',
        TemplateView.as_view(template_name='home_contratacao.html'),
        name='home_contratacao'),
    path('editar_usuario/',
        UpdateUsuarioContratacaoView.as_view(),
        name='editar_usuario_contratacao'),
    path('logout/',
        LogoutUsuarioContratacaoView.as_view(),
        name='logout_contratacao'),
    re_path(r'^contratos(/(?P<pk>\d+))?/$',
        GestaoContratoCRUDListView.as_view(),
        name='gestao_contrato'),
    # path('cancelar_contrato_assinado/',
    #     CancelarContratoAssinadoView.as_view(),
    #     name='cancelar_contrato')
]
