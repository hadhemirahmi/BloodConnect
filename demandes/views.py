from django.shortcuts import render
from django.http import HttpResponse
<<<<<<< HEAD
from django.shortcuts import render, redirect
from .forms import DemandeUrgenteForm
=======
>>>>>>> 6db3816a27896ce06d24296326c1bccc933beeb7

# Create your views here.

def index(request):
<<<<<<< HEAD
    
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



=======
    return HttpResponse("Welcome to the Demandes index.")
>>>>>>> 6db3816a27896ce06d24296326c1bccc933beeb7
