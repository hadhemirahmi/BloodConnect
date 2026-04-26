from django.urls import path
from . import views

urlpatterns = [
    path('ajouter/', views.DemandeCreateView.as_view(), name='ajouter_demande'),
    path('<int:pk>/modifier/', views.DemandeUpdateView.as_view(), name='modifier_demande'),
    path('<int:pk>/cloturer/', views.DemandeDeleteView.as_view(), name='cloturer_demande'),
    path('<int:pk>/reponses/', views.DemandeDetailView.as_view(), name='voir_reponses'),
    path('historique/', views.DemandeListView.as_view(), name='historique_demandes'),
]