from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from django.urls import reverse_lazy
from .models import DemandeUrgente, ReponseAppel
from .forms import DemandeUrgenteForm

from django.contrib import messages

class HospitalRoleMixin(UserPassesTestMixin):
    def test_func(self):
        if not (self.request.user.is_authenticated and self.request.user.role == 'hopital'):
            return False
        
        # Vérifier si l'hôpital est validé par l'admin
        hopital = getattr(self.request.user, 'hopital', None)
        if hopital and not hopital.valide:
            messages.warning(self.request, "Votre compte hôpital doit être validé par un administrateur avant de pouvoir publier des demandes.")
            return False
        return True
    
    def handle_no_permission(self):
        if self.request.user.is_authenticated and self.request.user.role == 'hopital':
            return redirect('dashboard_hopital')
        return redirect('login')

class DemandeCreateView(LoginRequiredMixin, HospitalRoleMixin, CreateView):
    model = DemandeUrgente
    form_class = DemandeUrgenteForm
    template_name = 'demandes/ajouter_demandes.html'
    success_url = reverse_lazy('historique_demandes')

    def form_valid(self, form):
        form.instance.hopital = self.request.user.hopital
        return super().form_valid(form)

class DemandeUpdateView(LoginRequiredMixin, HospitalRoleMixin, UpdateView):
    model = DemandeUrgente
    form_class = DemandeUrgenteForm
    template_name = 'demandes/modifier_demande.html'
    success_url = reverse_lazy('historique_demandes')

class DemandeCloturerView(LoginRequiredMixin, HospitalRoleMixin, UpdateView):
    model = DemandeUrgente
    fields = []  # No fields to edit via form
    template_name = 'demandes/cloturer_demande.html'
    success_url = reverse_lazy('historique_demandes')

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.statut = 'cloturee'
        self.object.save()
        messages.success(self.request, "La demande a été clôturée avec succès.")
        return redirect(self.get_success_url())

class DemandeDetailView(LoginRequiredMixin, HospitalRoleMixin, DetailView):
    model = DemandeUrgente
    template_name = 'demandes/voir_reponses.html'
    context_object_name = 'demande'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reponses'] = self.object.reponses.all().select_related('donneur__user')
        return context

class DemandeListView(LoginRequiredMixin, HospitalRoleMixin, ListView):
    model = DemandeUrgente
    template_name = 'demandes/historique_demandes.html'
    context_object_name = 'demandes'

    def get_queryset(self):
        return DemandeUrgente.objects.filter(hopital=self.request.user.hopital).order_by('-delai')

def index(request):
    return render(request, 'demandes/index.html')
