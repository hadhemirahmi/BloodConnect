from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.role == 'admin' or request.user.is_superuser):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Vous devez être administrateur.")
        return redirect('index')
    return _wrapped_view

def hospital_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'hopital' and hasattr(request.user, 'hopital'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Réservé aux hôpitaux avec un profil complet.")
        return redirect('index')
    return _wrapped_view

def hospital_validated_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'hopital':
            hopital = getattr(request.user, 'hopital', None)
            if hopital and hopital.valide:
                return view_func(request, *args, **kwargs)
            messages.warning(request, "Votre compte hôpital doit être validé par un administrateur pour effectuer cette action.")
            return redirect('dashboard_hopital')
        messages.error(request, "Accès refusé. Réservé aux hôpitaux.")
        return redirect('index')
    return _wrapped_view

def donor_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == 'donneur' and hasattr(request.user, 'donneur'):
            return view_func(request, *args, **kwargs)
        messages.error(request, "Accès refusé. Réservé aux donneurs avec un profil complet.")
        return redirect('index')
    return _wrapped_view
