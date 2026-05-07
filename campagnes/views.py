from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from .models import Campagne, Inscription
from django.urls import reverse_lazy
from .forms import CampagneForm
from core.utils import is_compatible
from core.decorators import donor_required, hospital_required, hospital_validated_required

class HospitalValidationMixin(UserPassesTestMixin):
    def test_func(self):
        if not (self.request.user.is_authenticated and self.request.user.role == 'hopital'):
            return False
        hopital = getattr(self.request.user, 'hopital', None)
        if hopital and not hopital.valide:
            messages.warning(self.request, "Votre compte hôpital doit être validé par un administrateur pour gérer des campagnes.")
            return False
        return True
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.role == 'hopital':
            return redirect('dashboard_hopital')
        return redirect('login')

class CampagneListView(ListView):
    model = Campagne
    template_name = 'campagnes/campagne_list.html'
    context_object_name = 'campagnes'
    
    def get_queryset(self):
        import datetime
        return Campagne.objects.filter(date__gte=datetime.date.today()).order_by('date')

class CampagneDetailView(DetailView):
    model = Campagne
    template_name = 'campagnes/campagne_detail.html'
    context_object_name = 'campagne'

class CampagneCreateView(LoginRequiredMixin, HospitalValidationMixin, CreateView):
    model = Campagne
    form_class = CampagneForm
    template_name = 'campagnes/campagne_form.html'
    success_url = reverse_lazy('dashboard_hopital')

    def form_valid(self, form):
        form.instance.hopital = self.request.user.hopital
        return super().form_valid(form)

class CampagneUpdateView(UpdateView):
    model = Campagne
    form_class = CampagneForm
    template_name = 'campagnes/campagne_form.html'
    success_url = reverse_lazy('dashboard_hopital')

class CampagneDeleteView(DeleteView):
    model = Campagne
    template_name = 'campagnes/campagne_confirm_delete.html'
    success_url = reverse_lazy('dashboard_hopital')

@login_required
@donor_required
def participer_campagne(request, campagne_id):
        
    donneur = request.user.donneur
    if not donneur.est_eligible():
        messages.error(request, f"Vous n'êtes pas encore éligible pour donner du sang. Votre prochaine date possible est le {donneur.prochaine_date_don}.")
        return redirect('dashboard_donneur')

    campagne = get_object_or_404(Campagne, pk=campagne_id)
    
    # Générer les créneaux (logique simple : 30 min par créneau à partir de 08:00)
    import datetime
    start_time = datetime.time(8, 0)
    slots = []
    for i in range(campagne.nb_creneaux):
        slot_start = (datetime.datetime.combine(datetime.date.today(), start_time) + datetime.timedelta(minutes=30*i)).time()
        slot_end = (datetime.datetime.combine(datetime.date.today(), slot_start) + datetime.timedelta(minutes=30)).time()
        slot_str = f"{slot_start.strftime('%H:%M')} - {slot_end.strftime('%H:%M')}"
        
        # Compter les inscriptions pour ce créneau
        nb_inscrits = campagne.inscriptions.filter(creneau_index=i).count()
        slots.append({
            'index': i,
            'time': slot_str,
            'full': nb_inscrits >= campagne.capacite_par_creneau,
            'nb_inscrits': nb_inscrits
        })

    if request.method == 'POST':
        try:
            creneau_index = int(request.POST.get('creneau_index'))
            if creneau_index < 0 or creneau_index >= campagne.nb_creneaux:
                messages.error(request, "Créneau invalide.")
                return redirect('participer_campagne', campagne_id=campagne.id)
            
            # Re-vérifier la capacité au moment de la soumission
            nb_inscrits = campagne.inscriptions.filter(creneau_index=creneau_index).count()
            if nb_inscrits >= campagne.capacite_par_creneau:
                messages.error(request, "Désolé, ce créneau vient d'être rempli.")
                return redirect('participer_campagne', campagne_id=campagne.id)
            
            # Vérifier si déjà inscrit
            if campagne.inscriptions.filter(donneur=donneur).exists():
                messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
                return redirect('dashboard_donneur')

            selected_slot = next(s for s in slots if s['index'] == creneau_index)
            
            Inscription.objects.create(
                campagne=campagne,
                donneur=donneur,
                creneau_index=creneau_index,
                creneau_horaire=selected_slot['time']
            )
            messages.success(request, f"Inscription confirmée pour le créneau {selected_slot['time']}.")
            return redirect('dashboard_donneur')
        except (ValueError, StopIteration):
            messages.error(request, "Une erreur est survenue lors de l'inscription.")
            return redirect('participer_campagne', campagne_id=campagne.id)

    return render(request, 'campagnes/participer_campagne.html', {
        'campagne': campagne,
        'slots': slots
    })

@login_required
def mes_campagnes(request):
    if request.user.role == 'donneur':
        inscriptions = Inscription.objects.filter(donneur=request.user.donneur).select_related('campagne')
        return render(request, 'campagnes/mes_campagnes_donneur.html', {'inscriptions': inscriptions})
    else:
        campagnes = request.user.hopital.campagnes.all().order_by('-date')
        return render(request, 'campagnes/mes_campagnes_hopital.html', {'campagnes': campagnes})

@login_required
@hospital_required
def inscriptions_campagne(request, campagne_id):
    
    campagne = get_object_or_404(Campagne, pk=campagne_id, hopital=request.user.hopital)
    inscriptions = campagne.inscriptions.all().select_related('donneur__user').order_by('creneau_index')
    
    return render(request, 'campagnes/inscriptions_campagne.html', {
        'campagne': campagne,
        'inscriptions': inscriptions
    })

@login_required
@hospital_validated_required
def valider_presence(request, inscription_id):
    
    inscription = get_object_or_404(Inscription, id=inscription_id, campagne__hopital=request.user.hopital)
    inscription.present = True
    inscription.save()
    
    # Mettre à jour la date du dernier don du donneur
    donneur = inscription.donneur
    donneur.derniere_don = inscription.campagne.date
    donneur.save()
    
    messages.success(request, f"Présence validée pour {donneur.user.get_full_name()}. Son éligibilité a été mise à jour.")
    return redirect('inscriptions_campagne', campagne_id=inscription.campagne.id)
