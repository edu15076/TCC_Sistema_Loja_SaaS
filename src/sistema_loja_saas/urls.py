"""
URL configuration for sistema_loja_saas project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from common.urls import urlpatterns as common_urls
from saas.urls import urlpatterns as saas_urls
from loja.urls import urlpatterns as loja_urls


urlpatterns = [
    path('admin/', admin.site.urls),
    *common_urls,
    *saas_urls,
    *loja_urls,
]
