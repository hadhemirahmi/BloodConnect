from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from comptes.models import Donneur, Hopital
from demandes.models import DemandeUrgente
from dons.models import Don
from django.db.models import Count, Sum
import csv
from django.http import HttpResponse, JsonResponse
from datetime import date
from .decorators import admin_required
import json
import google.generativeai as genai
from decouple import config

# Configuration de Gemini
try:
    genai.configure(api_key=config('GEMINI_API_KEY'))
except Exception as e:
    print("Erreur de configuration Gemini:", e)
def index(request):
    return render(request, 'accueil.html')

@login_required
@admin_required
def dashboard_admin(request):
    
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

# views.py

@login_required
@admin_required
def demandes_par_ville(request, ville):
    """Affiche la liste des demandes urgentes pour une ville spécifique"""
    
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

@login_required
@admin_required
def table_de_bord(request):
    """Affiche le tableau de bord avec les statistiques par groupe sanguin"""
    
    # Demandes actives par groupe sanguin
    demandes_par_groupe = DemandeUrgente.objects.filter(
        statut='active'
    ).values('groupe_sanguin').annotate(
        total_demandes=Count('id'),
        total_quantite=Sum('quantite')
    ).order_by('groupe_sanguin')
    
    # Dons par groupe sanguin (via la relation donneur)
    dons_par_groupe = Don.objects.select_related('donneur').values(
        'donneur__groupe_sanguin'
    ).annotate(
        total_dons=Count('id')
    ).order_by('donneur__groupe_sanguin')
    
    # Nettoyer les données (enlever les groupes None)
    dons_par_groupe_clean = []
    for item in dons_par_groupe:
        if item['donneur__groupe_sanguin']:
            dons_par_groupe_clean.append({
                'groupe_sanguin': item['donneur__groupe_sanguin'],
                'total_dons': item['total_dons']
            })
    
    # Toutes les demandes actives pour le tableau
    demandes_actives = DemandeUrgente.objects.filter(
        statut='active'
    ).select_related('hopital').order_by('-delai')[:10]
    
    # Donneurs par groupe sanguin
    donneurs_par_groupe = Donneur.objects.values('groupe_sanguin').annotate(
        total_donneurs=Count('id')
    ).order_by('groupe_sanguin')
    
    context = {
        'total_donneurs': Donneur.objects.count(),
        'total_dons': Don.objects.count(),
        'total_demandes_actives': DemandeUrgente.objects.filter(statut='active').count(),
        'total_hopitaux': Hopital.objects.count(),
        'hopitaux_en_attente': Hopital.objects.filter(valide=False).count(),
        'demandes_par_groupe': demandes_par_groupe,
        'dons_par_groupe': dons_par_groupe_clean,
        'donneurs_par_groupe': donneurs_par_groupe,
        'demandes_actives': demandes_actives,
    }
    
    return render(request, "core/Table_de_bord.html", context)
@login_required
@admin_required
def csv_donneurs(request):
    """Affiche la page d'export CSV des donneurs (admin uniquement)"""
    
    # Récupérer tous les donneurs
    donneurs = Donneur.objects.select_related('user').all().order_by('groupe_sanguin', 'user__username')
    
    context = {
        'donneurs': donneurs,
        'total_donneurs': donneurs.count(),
    }
    
    return render(request, "core/CSV.html", context)


@login_required
@admin_required
def exporter_donneurs_csv(request):
    """Exporte la liste des donneurs au format CSV"""
    
    # Créer la réponse HTTP avec le type CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="donneurs_bloodconnect.csv"'
    
    # Créer le writer CSV
    writer = csv.writer(response, delimiter=';')
    
    # En-têtes du fichier CSV
    writer.writerow([
        'ID',
        'Nom d\'utilisateur',
        'Email',
        'Groupe sanguin',
        'Sexe',
        'Date de naissance',
        'Âge',
        'Ville',
        'Statut',
        'Dernier don',
        'Prochaine date éligible'
    ])
    
    # Récupérer tous les donneurs avec leurs informations utilisateur
    donneurs = Donneur.objects.select_related('user').all().order_by('groupe_sanguin', 'user__username')
    
    # Ajouter les données des donneurs
    for donneur in donneurs:
        # Calculer l'âge
        age = None
        if donneur.date_naissance:
            today = date.today()
            age = today.year - donneur.date_naissance.year - ((today.month, today.day) < (donneur.date_naissance.month, donneur.date_naissance.day))
        
        writer.writerow([
            donneur.id,
            donneur.user.username,
            donneur.user.email,
            donneur.groupe_sanguin,
            donneur.sexe,
            donneur.date_naissance.strftime('%d/%m/%Y') if donneur.date_naissance else '',
            age if age else '',
            donneur.ville,
            'Actif' if donneur.actif else 'Inactif',
            donneur.derniere_don.strftime('%d/%m/%Y') if donneur.derniere_don else 'Aucun don',
            donneur.prochaine_date_don.strftime('%d/%m/%Y') if donneur.prochaine_date_don else 'Immédiatement',
        ])
    
    return response

def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            
            if not message:
                return JsonResponse({'error': 'Message vide'}, status=400)
                
            model = genai.GenerativeModel('gemini-flash-latest')
            
            # Prompt contextuel
            prompt = (
                "Tu es le Dr. BloodConnect, un assistant médical aimable et expert pour la plateforme de don de sang BloodConnect. "
                "Tu dois répondre aux questions concernant l'éligibilité au don de sang, les délais après certains événements "
                "(tatouages, vaccins, soins dentaires, voyages), et le processus de don. "
                "Si la question n'est pas liée à la santé ou au don de sang, redirige poliment la conversation vers ce sujet. "
                "Réponds en français, de manière claire et concise.\n\n"
                f"Question de l'utilisateur : {message}"
            )
            
            response = model.generate_content(prompt)
            
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            print("Erreur Gemini:", e)
            return JsonResponse({'error': 'Désolé, je rencontre des difficultés techniques pour vous répondre en ce moment.'}, status=500)
            
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
