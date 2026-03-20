from django.db import models

GROUPE_SANGUIN_CHOICES = [
    ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
    ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
]

SEXE_CHOICES = [('M', 'Homme'), ('F', 'Femme')]

STATUT_DEMANDE_CHOICES = [('active', 'Active'), ('cloturee', 'Clôturée')]
STATUT_REPONSE_CHOICES = [
    ('en_attente', 'En attente'),
    ('acceptee', 'Acceptée'),
    ('refusee', 'Refusée'),
]