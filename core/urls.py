from django.urls import path,include
from . import views
urlpatterns = [
    path('', views.index, name='index'),
    path('admin-dashboard/', views.dashboard_admin, name='admin_dashboard'),
]
