from django.urls import path
from django.views.generic import TemplateView

from .views import *


urlpatterns = [
    path('criar_usuario/', CreateUsuarioView.as_view(), name='criar_usuario'),
    path('login/', LoginUsuarioView.as_view(), name='login'),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
]
