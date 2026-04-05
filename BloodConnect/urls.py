"""
URL configuration for BloodConnect project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
<<<<<<< HEAD
from django.urls import path
from . import views


urlpatterns = [
    # Page d'accueil
    path('', views.accueil, name='accueil'),

    # Admin
    path('admin/', admin.site.urls),

    # Apps du projet
=======


urlpatterns = [
    path('admin/', admin.site.urls),
>>>>>>> 6db3816a27896ce06d24296326c1bccc933beeb7
    path('comptes/', include('comptes.urls')),
    path('demandes/', include('demandes.urls')),
    path('dons/', include('dons.urls')),
    path('campagnes/', include('campagnes.urls')),
    path('core/', include('core.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
