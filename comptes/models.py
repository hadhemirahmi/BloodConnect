from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Donneur(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    groupe_sanguin = models.CharField(max_length=3, choices=[
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
])
    sexe = models.CharField(max_length=1, choices=[('M', 'Homme'), ('F', 'Femme')])
    date_naissance = models.DateField()
    ville = models.CharField(max_length=100)
    actif = models.BooleanField(default=True)
    derniere_don = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.groupe_sanguin})"

    @property
    def prochaine_date_don(self):
        if not self.derniere_don:
            return "Immédiatement"
        jours = 56 if self.sexe == 'M' else 84
        return self.derniere_don + timedelta(days=jours)

    def est_eligble(self):
        if not self.derniere_don:
            return True
        jours = 56 if self.sexe == 'M' else 84
        return (timezone.now().date() - self.derniere_don) >= timedelta(days=jours)


class Hopital(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nom = models.CharField(max_length=200)
    adresse = models.CharField(max_length=300)
    ville = models.CharField(max_length=100)
    agrement = models.CharField(max_length=50, unique=True)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return self.nom