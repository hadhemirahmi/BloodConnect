
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from .models import User, Donneur, Hopital
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
def register_donneur(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password1'],
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
        )

        user.role = "donneur"
        user.save()

        Donneur.objects.create(
            user=user,
            groupe_sanguin=request.POST['groupe_sanguin'],
            sexe=request.POST['sexe'],
            date_naissance=request.POST['date_naissance'],
            ville=request.POST['ville'],
        )

        messages.success(request, "Compte donneur créé avec succès")
        return redirect("login")

    return render(request, "comptes/register_donneur.html")
def register_hopital(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password1'],
        )

        user.role = "hopital"
        user.is_active = False  # ⚠️ attente validation admin
        user.save()

        Hopital.objects.create(
            user=user,
            nom=request.POST['nom'],
            adresse=request.POST['adresse'],
            ville=request.POST['ville'],
            agrement=request.POST['agrement'],
            valide=False
        )

        messages.success(request, "Compte envoyé pour validation")
        return redirect("login")

    return render(request, "comptes/register_hopital.html")
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            # 🎯 redirection selon rôle
            if user.role == "donneur":
                return redirect("dashboard_donneur")
            elif user.role == "hopital":
                return redirect("dashboard_hopital")
            elif user.role == "admin":
                return redirect("dashboard_admin")

        return render(request, "comptes/login.html", {"error": "Identifiants incorrects"})

    return render(request, "comptes/login.html")
def logout_view(request):
    logout(request)
    return redirect("login")
