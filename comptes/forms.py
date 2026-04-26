from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Donneur, Hopital


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Votre identifiant',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': '••••••••',
        })
    )


class DonneurRegistrationForm(forms.Form):
    # Champs User
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: ahmed123'})
    )
    first_name = forms.CharField(
        label='Prénom',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Nom',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Champs Donneur
    groupe_sanguin = forms.ChoiceField(
        label='Groupe sanguin',
        choices=[('A+','A+'),('A-','A-'),('B+','B+'),('B-','B-'),
                 ('AB+','AB+'),('AB-','AB-'),('O+','O+'),('O-','O-')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    sexe = forms.ChoiceField(
        label='Sexe',
        choices=[('M','Homme'), ('F','Femme')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    date_naissance = forms.DateField(
        label='Date de naissance',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    ville = forms.CharField(
        label='Ville',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
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
        )
        Donneur.objects.create(
            user=user,
            groupe_sanguin=data['groupe_sanguin'],
            sexe=data['sexe'],
            date_naissance=data['date_naissance'],
            ville=data['ville'],
        )
        return user


class HopitalRegistrationForm(forms.Form):
    # Champs User
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: chu_rabta'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password2 = forms.CharField(
        label='Confirmer le mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Champs Hopital
    nom = forms.CharField(
        label="Nom de l'établissement",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    adresse = forms.CharField(
        label='Adresse',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    ville = forms.CharField(
        label='Ville',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    agrement = forms.CharField(
        label="Numéro d'agrément",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ex: TN-2024-0001'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur est déjà pris.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet email est déjà utilisé.")
        return email

    def clean_agrement(self):
        agrement = self.cleaned_data['agrement']
        if Hopital.objects.filter(agrement=agrement).exists():
            raise forms.ValidationError("Ce numéro d'agrément est déjà enregistré.")
        return agrement

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('password1') != cleaned_data.get('password2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return cleaned_data

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1'],
            first_name=data['nom'],
        )
        Hopital.objects.create(
            user=user,
            nom=data['nom'],
            adresse=data['adresse'],
            ville=data['ville'],
            agrement=data['agrement'],
            valide=False,  # En attente de validation admin
        )
        return user