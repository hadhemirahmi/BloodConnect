from django.shortcuts import render

# Vue pour la page d'accueil
def accueil(request):
    return render(request, 'accueil.html')

# Vue pour la page À Propos
def about(request):
    return render(request, 'about.html')
