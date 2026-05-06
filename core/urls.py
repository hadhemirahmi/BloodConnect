from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.dashboard_admin, name='admin_dashboard'),
    path('admin/demandes/ville/<str:ville>/', views.demandes_par_ville, name='Demandes_parV'),
    
]
