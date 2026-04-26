from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from .models import Donneur, Hopital
from .forms import DonneurRegistrationForm, HopitalRegistrationForm

User = get_user_model()
def register_view(request):
    role = request.GET.get('role', 'donneur')
    
    if request.method == "POST":
        role = request.POST.get('role', 'donneur')
        if role == 'hopital':
            form = HopitalRegistrationForm(request.POST)
        else:
            form = DonneurRegistrationForm(request.POST)
            
        if form.is_valid():
            form.save()
            if role == 'hopital':
                messages.success(request, "Votre demande a été envoyée pour validation.")
            else:
                messages.success(request, "Compte créé avec succès !")
            return redirect("login")
    else:
        if role == 'hopital':
            form = HopitalRegistrationForm()
        else:
            form = DonneurRegistrationForm()

    return render(request, "comptes/registration/register.html", {
        "form": form,
        "role": role
    })
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_active:
                messages.warning(request, "Attention : Votre compte n'est pas encore activé ou est en attente de validation.")
                return render(request, "comptes/registration/login.html", {"error": "Compte inactif"})
            
            login(request, user)
            
            # Redirection dynamique selon le rôle
            if user.is_superuser:
                return redirect("/admin/")
            
            if user.role == "donneur":
                return redirect("dashboard_donneur")
            elif user.role == "hopital":
                return redirect("dashboard_hopital")
            elif user.role == "admin":
                return redirect("dashboard_admin")
            else:
                return redirect("index")

        return render(request, "comptes/registration/login.html", {"error": "Identifiants ou rôle incorrects"})

    return render(request, "comptes/registration/login.html")
def logout_view(request):
    logout(request)
    return redirect("login")

from django.contrib.auth.decorators import login_required

@login_required
def dashboard_donneur(request):
    return render(request, "dons/dashboard_donneur.html", {
        "donneur": request.user.donneur
    })

@login_required
def dashboard_hopital(request):
    return render(request, "demandes/dashboard_hopital.html", {
        "hopital": request.user.hopital
    })

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('login')
    return render(request, "core/dashboard_admin.html")
