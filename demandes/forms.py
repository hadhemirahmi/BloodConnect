from django import forms
from .models import DemandeUrgente

class DemandeUrgenteForm(forms.ModelForm):
    class Meta:
        model = DemandeUrgente
        fields = ['groupe_sanguin', 'quantite', 'delai', 'description']

        widgets = {
            'delai': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }