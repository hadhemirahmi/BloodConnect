from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from .models import Donneur, Hopital

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class DonneurRegistrationForm(forms.Form):
   
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label="Prénom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label="Nom", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    groupe_sanguin = forms.ChoiceField(
        label="Groupe sanguin",
        choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sexe = forms.ChoiceField(label="Sexe", choices=[('M', 'Homme'), ('F', 'Femme')], widget=forms.Select(attrs={'class': 'form-control'}))
    date_naissance = forms.DateField(label="Date de naissance", widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    ville = forms.CharField(label="Ville", widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
      
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role='donneur'
        )
       
        Donneur.objects.create(
            user=user,
            groupe_sanguin=data['groupe_sanguin'],
            sexe=data['sexe'],
            date_naissance=data['date_naissance'],
            ville=data['ville']
        )
        return user
class DonneurUpdateForm(forms.ModelForm):
    class Meta:
        model = Donneur
        fields = ['groupe_sanguin', 'sexe', 'date_naissance', 'ville']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'groupe_sanguin': forms.Select(attrs={'class': 'form-control'}),
            'sexe': forms.Select(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
        }

class HopitalUpdateForm(forms.ModelForm):
    class Meta:
        model = Hopital
        fields = ['nom', 'adresse', 'ville', 'agrement']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.TextInput(attrs={'class': 'form-control'}),
            'ville': forms.TextInput(attrs={'class': 'form-control'}),
            'agrement': forms.TextInput(attrs={'class': 'form-control'}),
        }

class HopitalRegistrationForm(forms.Form):
  
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    nom = forms.CharField(label="Nom de l'établissement", widget=forms.TextInput(attrs={'class': 'form-control'}))
    adresse = forms.CharField(label="Adresse", widget=forms.TextInput(attrs={'class': 'form-control'}))
    ville = forms.CharField(label="Ville", widget=forms.TextInput(attrs={'class': 'form-control'}))
    agrement = forms.CharField(label="Numéro d'agrément", widget=forms.TextInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 != p2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
            first_name=data['nom'],
            role='hopital',
            is_active=False
        )
        Hopital.objects.create(
            user=user,
            nom=data['nom'],
            adresse=data['adresse'],
            ville=data['ville'],
            agrement=data['agrement'],
            valide=False
        )
        return user