from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView 
from django.urls import reverse_lazy
from .models import DemandeUrgente, ReponseAppel
from .forms import DemandeUrgenteForm

class HospitalRoleMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'hopital'
    
    def handle_no_permission(self):
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

class DemandeDeleteView(LoginRequiredMixin, HospitalRoleMixin, DeleteView):
    model = DemandeUrgente
    template_name = 'demandes/cloturer_demande.html'
    success_url = reverse_lazy('historique_demandes')

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
