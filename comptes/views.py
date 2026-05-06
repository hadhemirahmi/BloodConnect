from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, get_user_model
from .models import Donneur, Hopital
from .forms import DonneurRegistrationForm, HopitalRegistrationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import user_passes_test

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
                return redirect("admin_dashboard")
            
            if user.role == "donneur":
                return redirect("dashboard_donneur")
            elif user.role == "hopital":
                return redirect("dashboard_hopital")
            elif user.role == "admin":
                return redirect("admin_dashboard")
            else:
                return redirect("accueil")

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
    
    # Inscriptions aux campagnes (Rappels)
    from campagnes.models import Inscription
    from django.utils import timezone
    prochaines_inscriptions = Inscription.objects.filter(
        donneur=donneur,
        campagne__date__gte=timezone.now().date()
    ).select_related('campagne').order_by('campagne__date')
    
    return render(request, "dons/dashboard_donneur.html", {
        "donneur": donneur,
        "demandes_compatibles": demandes_compatibles,
        "historique_dons": historique_dons,
        "prochaines_inscriptions": prochaines_inscriptions,
    })

@login_required
def dashboard_hopital(request):
    if not hasattr(request.user, 'hopital'):
        messages.error(request, "Accès refusé : Ce compte n'est pas configuré comme un hôpital.")
        return redirect('accueil')
    
    hopital = request.user.hopital
        
    demandes_actives = hopital.demandes.filter(statut='active')
    return render(request, "demandes/dashboard_hopital.html", {
        "hopital": hopital,
        "demandes_actives": demandes_actives
    })

@login_required
def profile_update(request):
    if request.user.role == 'donneur':
        if not hasattr(request.user, 'donneur'):
            messages.error(request, "Profil donneur introuvable.")
            return redirect('accueil')
        from .forms import DonneurUpdateForm
        instance = request.user.donneur
        form_class = DonneurUpdateForm
    else:
        if not hasattr(request.user, 'hopital'):
            messages.error(request, "Profil hôpital introuvable.")
            return redirect('accueil')
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
def toggle_donor_active(request):
    if request.user.role == 'donneur':
        donneur = request.user.donneur
        donneur.actif = not donneur.actif
        donneur.save()
        status = "réactivé" if donneur.actif else "désactivé (indisponible)"
        messages.success(request, f"Votre compte a été {status}.")
    return redirect('dashboard_donneur')





def is_admin(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(is_admin)
def valider_hopitaux_page(request):
    hopitaux_en_attente = Hopital.objects.filter(valide=False).select_related('user')
    hopitaux_valides    = Hopital.objects.filter(valide=True).select_related('user')
    return render(request, 'core/valider_hopitaux.html', {
        'hopitaux_en_attente': hopitaux_en_attente,
        'hopitaux_valides'   : hopitaux_valides,
    })

@user_passes_test(is_admin)
def valider_hopital(request, hopital_id):
    hopital = get_object_or_404(Hopital, id=hopital_id)
    hopital.valide = True
    hopital.user.is_active = True
    hopital.user.save()
    hopital.save()
    messages.success(request, f"✅ {hopital.nom} validé avec succès.")
    return redirect('valider_hopitaux')

@user_passes_test(is_admin)
def rejeter_hopital(request, hopital_id):
    hopital = get_object_or_404(Hopital, id=hopital_id)
    nom = hopital.nom
    hopital.user.delete()
    messages.error(request, f"❌ {nom} rejeté et supprimé.")
    return redirect('valider_hopitaux')
    