from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Don
from .forms import DonForm
from demandes.models import DemandeUrgente, ReponseAppel

@login_required
def enregistrer_don(request):
    if request.user.role != 'donneur':
        return redirect('index')
        
    if request.method == 'POST':
        form = DonForm(request.POST)
        if form.is_valid():
            don = form.save(commit=False)
            don.donneur = request.user.donneur
            don.save()

            donneur = request.user.donneur
            donneur.derniere_don = don.date_don
            donneur.save()
            
            messages.success(request, "Don enregistré avec succès. Merci pour votre générosité !")
            return redirect('dashboard_donneur')
    else:
        form = DonForm()
    return render(request, 'dons/enregistrer_don.html', {'form': form})

@login_required
def repondre_appel(request, pk):
    if request.user.role != 'donneur':
        return redirect('index')
        
    demande = get_object_or_404(DemandeUrgente, pk=pk, statut='active')
    
    # Vérifier si déjà répondu
    if ReponseAppel.objects.filter(demande=demande, donneur=request.user.donneur).exists():
        messages.info(request, "Vous avez déjà répondu à cet appel.")
    else:
        ReponseAppel.objects.create(demande=demande, donneur=request.user.donneur)
        messages.success(request, "Votre intention de don a été transmise à l'hôpital.")
        
    return redirect('dashboard_donneur')

@login_required
def liste_appels_compatibles(request):
    if request.user.role != 'donneur':
        return redirect('index')
    
    donneur = request.user.donneur
    # Logique de compatibilité sanguine (Qui peut donner à qui)
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
    target_groups = compatibility_map.get(donneur.groupe_sanguin, [donneur.groupe_sanguin])
    
    appels = DemandeUrgente.objects.filter(
        groupe_sanguin__in=target_groups,
        statut='active'
    ).order_by('-delai')
    
    return render(request, 'dons/liste_appels.html', {'appels': appels})