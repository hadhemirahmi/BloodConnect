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
