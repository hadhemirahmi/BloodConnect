from django.urls import path
from . import views

urlpatterns = [
    path('list/', views.CampagneListView.as_view(), name='campagne_list'),
    path('creer/', views.CampagneCreateView.as_view(), name='creer_campagne'),
    path('<int:pk>/', views.CampagneDetailView.as_view(), name='detail_campagne'),
    path('<int:pk>/modifier/', views.CampagneUpdateView.as_view(), name='modifier_campagne'),
    path('<int:pk>/supprimer/', views.CampagneDeleteView.as_view(), name='supprimer_campagne'),
    path('mes_campagnes/', views.mes_campagnes, name='mes_campagnes'),
    path('participer/<int:campagne_id>/', views.participer_campagne, name='participer_campagne'),
]
