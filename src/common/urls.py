from django.urls import path
from django.views.generic import TemplateView

from .views import *

urlpatterns = [
    path(
        'acesso-nao-autorizado/',
        TemplateView.as_view(template_name="acesso_nao_autorizado.html"),
        name='acesso_nao_autorizado',
    ),
]
