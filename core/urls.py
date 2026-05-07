from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.dashboard_admin, name='admin_dashboard'),

    path('csv-donneurs/', views.csv_donneurs, name='csv_donneurs'),
    path('exporter-donneurs-csv/', views.exporter_donneurs_csv, name='exporter_donneurs_csv'),
    path('carte-demandes/', views.carte_demandes, name='carte_demandes'),
    path('admin/demandes/ville/<str:ville>/', views.demandes_par_ville, name='Demandes_parV'),
    path('table-de-bord/', views.table_de_bord, name='table_de_bord'),

]


 