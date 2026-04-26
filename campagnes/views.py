from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from .models import Campagne, Inscription
from django.urls import reverse_lazy
from .forms import CampagneForm

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

class CampagneCreateView(CreateView):
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
def participer_campagne(request, campagne_id):
    if request.user.role != 'donneur':
        return redirect('index')
        
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
        creneau_index = int(request.POST.get('creneau_index'))
        selected_slot = next(s for s in slots if s['index'] == creneau_index)
        
        if selected_slot['full']:
            messages.error(request, "Ce créneau est complet.")
        elif campagne.inscriptions.filter(donneur=request.user.donneur).exists():
            messages.warning(request, "Vous êtes déjà inscrit à cette campagne.")
        else:
            Inscription.objects.create(
                campagne=campagne,
                donneur=request.user.donneur,
                creneau_index=creneau_index,
                creneau_horaire=selected_slot['time']
            )
            messages.success(request, f"Inscription confirmée pour le créneau {selected_slot['time']}.")
            return redirect('dashboard_donneur')

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
        campagnes = request.user.hopital.campagnes.all()
        return render(request, 'campagnes/mes_campagnes_hopital.html', {'campagnes': campagnes})

