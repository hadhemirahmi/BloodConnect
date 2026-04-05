from django import forms
from .models import DemandeUrgente

class DemandeUrgenteForm(forms.ModelForm):
    class Meta:
        model = DemandeUrgente
        fields = ['hopital', 'groupe_sanguin', 'quantite', 'delai', 'statut', 'description']

        widgets = {
            'delai': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }