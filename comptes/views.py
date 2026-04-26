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
    from demandes.models import DemandeUrgente
    from dons.models import Don
    donneur = request.user.donneur
    
    # Logique de compatibilité sanguine (Qui peut donner à qui)
    donneur_group = donneur.groupe_sanguin
    compatibility_map = {
        'O-': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
        'O+': ['O+', 'A+', 'B+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'A+': ['A+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'AB-': ['AB-', 'AB+'],
        'AB+': ['AB+'],
    }
    target_groups = compatibility_map.get(donneur_group, [donneur_group])
    
    demandes_compatibles = DemandeUrgente.objects.filter(
        groupe_sanguin__in=target_groups,
        statut='active'
    ).order_by('-delai')[:5]
    
    # Historique des dons
    historique_dons = donneur.dons.all().order_by('-date_don')
    
    return render(request, "dons/dashboard_donneur.html", {
        "donneur": donneur,
        "demandes_compatibles": demandes_compatibles,
        "historique_dons": historique_dons,
    })

@login_required
def dashboard_hopital(request):
    hopital = request.user.hopital
    demandes_actives = hopital.demandes.filter(statut='active')
    return render(request, "demandes/dashboard_hopital.html", {
        "hopital": hopital,
        "demandes_actives": demandes_actives
    })

@login_required
def profile_update(request):
    if request.user.role == 'donneur':
        from .forms import DonneurUpdateForm
        instance = request.user.donneur
        form_class = DonneurUpdateForm
    else:
        from .forms import HopitalUpdateForm
        instance = request.user.hopital
        form_class = HopitalUpdateForm
        
    if request.method == 'POST':
        form = form_class(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('dashboard_donneur' if request.user.role == 'donneur' else 'dashboard_hopital')
    else:
        form = form_class(instance=instance)
        
    return render(request, "comptes/profile_update.html", {"form": form})
@login_required
def profile(request):
    return render(request, "comptes/profile.html")
@login_required
def dashboard_admin(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('login')
    return render(request, "core/dashboard_admin.html")

@login_required
def toggle_donor_active(request):
    if request.user.role == 'donneur':
        donneur = request.user.donneur
        donneur.actif = not donneur.actif
        donneur.save()
        status = "réactivé" if donneur.actif else "désactivé (indisponible)"
        messages.success(request, f"Votre compte a été {status}.")
    return redirect('dashboard_donneur')
