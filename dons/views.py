from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Don
from .forms import DonForm
from demandes.models import DemandeUrgente, ReponseAppel
from core.utils import get_compatible_groups, is_compatible
from core.decorators import donor_required

@login_required
@donor_required
def enregistrer_don(request):
        
    donneur = request.user.donneur
    if not donneur.est_eligible():
        messages.error(request, f"Vous n'êtes pas encore éligible pour enregistrer un don. Prochaine date : {donneur.prochaine_date_don}")
        return redirect('dashboard_donneur')

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
@donor_required
def repondre_appel(request, pk):
        
    donneur = request.user.donneur
    if not donneur.est_eligible():
        messages.error(request, f"Vous n'êtes pas encore éligible pour répondre à cet appel. Prochaine date : {donneur.prochaine_date_don}")
        return redirect('dashboard_donneur')

    demande = get_object_or_404(DemandeUrgente, pk=pk, statut='active')
    
    # Vérifier la compatibilité
    if not is_compatible(donneur.groupe_sanguin, demande.groupe_sanguin):
        messages.error(request, f"Votre groupe sanguin ({donneur.groupe_sanguin}) n'est pas compatible avec cette demande ({demande.groupe_sanguin}).")
        return redirect('liste_appels_compatibles')

    # Vérifier si déjà répondu
    if ReponseAppel.objects.filter(demande=demande, donneur=donneur).exists():
        messages.info(request, "Vous avez déjà répondu à cet appel.")
    else:
        ReponseAppel.objects.create(demande=demande, donneur=donneur)
        messages.success(request, "Votre intention de don a été transmise à l'hôpital.")
        
    return redirect('dashboard_donneur')

@login_required
@donor_required
def liste_appels_compatibles(request):
    
    donneur = request.user.donneur
    target_groups = get_compatible_groups(donneur.groupe_sanguin)
    
    appels = DemandeUrgente.objects.filter(
        groupe_sanguin__in=target_groups,
        statut='active'
    ).order_by('-delai')
    
    return render(request, 'dons/liste_appels.html', {'appels': appels})

@login_required
@donor_required
def historique_dons(request):
    
    dons = Don.objects.filter(donneur=request.user.donneur).order_by('-date_don')
    return render(request, 'dons/historique_dons.html', {'dons': dons})