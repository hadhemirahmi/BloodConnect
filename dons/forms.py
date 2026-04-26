from django import forms
from .models import Don

class DonForm(forms.ModelForm):
    class Meta:
        model = Don
        fields = ['hopital', 'date_don', 'notes']
        widgets = {
            'date_don': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }