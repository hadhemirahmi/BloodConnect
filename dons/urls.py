from django.urls import path
from . import views

urlpatterns = [
    path('enregistrer/', views.enregistrer_don, name='enregistrer_don'),
    path('repondre/<int:pk>/', views.repondre_appel, name='repondre_appel'),
    path('appels-compatibles/', views.liste_appels_compatibles, name='compatible_calls'),
]