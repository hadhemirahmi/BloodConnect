from django.urls import path,include
from . import views
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # 🩸 Inscription donneur
    path("register/donneur/", views.register_donneur, name="register_donneur"),

    # 🏥 Inscription hôpital
    path("register/hopital/", views.register_hopital, name="register_hopital"),
 ]
