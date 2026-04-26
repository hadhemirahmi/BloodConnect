from django import forms
from .models import Campagne

class CampagneForm(forms.ModelForm):
    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_par_creneau', 'nb_creneaux']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }