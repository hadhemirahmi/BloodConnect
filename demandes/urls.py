from django.urls import path,include
from . import views
urlpatterns = [
<<<<<<< HEAD
 path('', views.index, name='accueilD'),
 path('ajouter_demandes/', views.ajouter_demande, name='ajouter_demandes')
=======
 path('', views.index, name='index'),
>>>>>>> 6db3816a27896ce06d24296326c1bccc933beeb7
 ]
