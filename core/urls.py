from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.dashboard_admin, name='admin_dashboard'),
    path('exporter-donneurs/', views.exporter_donneurs_csv, name='exporter_donneurs_csv'),
    path('carte-demandes/', views.carte_demandes, name='carte_demandes'),
    
]
