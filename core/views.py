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
    
    from django.db.models import Count
    
    # Statistiques par groupe sanguin pour les demandes actives
    stats_groupes = DemandeUrgente.objects.filter(statut='active').values('groupe_sanguin').annotate(total=Count('id'))
    
    context = {
        'total_donneurs': Donneur.objects.count(),
        'total_hopitaux': Hopital.objects.count(),
        'total_demandes_actives': DemandeUrgente.objects.filter(statut='active').count(),
        'total_dons': Don.objects.count(),
        'stats_groupes': stats_groupes,
        'derniers_donneurs': Donneur.objects.order_by('-id')[:5],
        'derniers_hopitaux': Hopital.objects.filter(valide=False)[:5],
        'dernieres_demandes': DemandeUrgente.objects.order_by('-id')[:5],
    }
    
    return render(request, "core/dashboard_admin.html", context)

import csv
from django.http import HttpResponse

@login_required
def exporter_donneurs_csv(request):
    if not request.user.is_superuser and request.user.role != 'admin':
        return redirect('login')
        
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="liste_donneurs.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Prénom', 'Email', 'Groupe Sanguin', 'Ville', 'Sexe', 'Date Naissance', 'Actif'])
    
    donneurs = Donneur.objects.all().select_related('user')
    for d in donneurs:
        writer.writerow([
            d.user.last_name,
            d.user.first_name,
            d.user.email,
            d.groupe_sanguin,
            d.ville,
            d.sexe,
            d.date_naissance,
            'Oui' if d.actif else 'Non'
        ])
        
    return response

@login_required
def carte_demandes(request):
    # Regrouper les demandes urgentes par ville (via l'hôpital)
    demandes_par_ville = DemandeUrgente.objects.filter(statut='active').values('hopital__ville').annotate(total=Count('id')).order_by('hopital__ville')
    
    # Détails pour chaque ville
    villes_data = []
    for item in demandes_par_ville:
        ville = item['hopital__ville']
        demandes = DemandeUrgente.objects.filter(statut='active', hopital__ville=ville)
        villes_data.append({
            'ville': ville,
            'total': item['total'],
            'demandes': demandes
        })
        
    return render(request, "core/Demandes_parV.html", {'villes_data': villes_data})
