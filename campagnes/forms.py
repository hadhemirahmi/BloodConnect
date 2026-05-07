from django import forms
from .models import Campagne

class CampagneForm(forms.ModelForm):
    GROUPE_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    groupes_cibles = forms.MultipleChoiceField(
        choices=GROUPE_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        label="Groupes sanguins ciblés"
    )

    class Meta:
        model = Campagne
        fields = ['nom', 'date', 'lieu', 'groupes_cibles', 'capacite_par_creneau', 'nb_creneaux']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.groupes_cibles:
            self.initial['groupes_cibles'] = self.instance.groupes_cibles.split(',')

    def clean_groupes_cibles(self):
        data = self.cleaned_data['groupes_cibles']
        return ','.join(data)

    def clean_capacite_par_creneau(self):
        val = self.cleaned_data['capacite_par_creneau']
        if val < 1:
            raise forms.ValidationError("La capacité doit être d'au moins 1 personne.")
        return val

    def clean_nb_creneaux(self):
        val = self.cleaned_data['nb_creneaux']
        if val < 1:
            raise forms.ValidationError("Il doit y avoir au moins 1 créneau.")
        return val