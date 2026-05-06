from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from comptes.models import Donneur, Hopital
from demandes.models import DemandeUrgente
from dons.models import Don

def index(request):
    return render(request, 'accueil.html')

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('login')
    
    context = {
        'total_donneurs': Donneur.objects.count(),
        'total_hopitaux': Hopital.objects.count(),
        'total_demandes_actives': DemandeUrgente.objects.filter(statut='active').count(),
        'total_dons': Don.objects.count(),
        'derniers_donneurs': Donneur.objects.order_by('-id')[:5],
        'derniers_hopitaux': Hopital.objects.filter(valide=False)[:5], # Show hospitals pending validation
        'dernieres_demandes': DemandeUrgente.objects.order_by('-id')[:5],
    }
    
    return render(request, "core/dashboard_admin.html", context)
# views.py

@login_required
def demandes_par_ville(request, ville):
    """Affiche la liste des demandes urgentes pour une ville spécifique"""
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('login')
    
    ville_recherchee = ville
    
    # Gérer la recherche via POST ou GET
    if request.method == 'GET' and 'ville' in request.GET:
        ville_recherchee = request.GET.get('ville')
    
    # Si ville = 'toutes' ou vide, afficher toutes les demandes
    if ville_recherchee == 'toutes' or not ville_recherchee:
        demandes = DemandeUrgente.objects.filter(statut='active').select_related('hopital')
        ville_affichee = "Toutes les villes"
    else:
        # Filtrer par ville (insensible à la casse)
        demandes = DemandeUrgente.objects.filter(
            statut='active',
            hopital__ville__iexact=ville_recherchee
        ).select_related('hopital')
        ville_affichee = ville_recherchee
    
    return render(request, "core/Demandes_parV.html", {
        'demandes': demandes,
        'ville': ville_affichee,
        'ville_affichee': ville_affichee
    })



  
