from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import DemandeUrgenteForm


# Create your views here.

def index(request):
    
    return render(request, 'accueilD.html')

def ajouter_demande(request):
    if request.method == 'POST':
        form = DemandeUrgenteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('liste_demandes')
    else:
        form = DemandeUrgenteForm()

    return render(request, 'ajouter_demandes.html', {'form': form})

    
    

