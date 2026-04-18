from django.urls import path,include
from . import views
urlpatterns = [
 path('', views.index, name='accueilD'),
 path('ajouter_demandes/', views.ajouter_demande, name='ajouter_demandes')
 ]
