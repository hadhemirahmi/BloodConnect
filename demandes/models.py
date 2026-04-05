from django.db import models
from core.models import GROUPE_SANGUIN_CHOICES, STATUT_DEMANDE_CHOICES, STATUT_REPONSE_CHOICES

class DemandeUrgente(models.Model):
    hopital = models.ForeignKey('comptes.Hopital', on_delete=models.CASCADE, related_name='demandes')
    groupe_sanguin = models.CharField(max_length=3, choices=GROUPE_SANGUIN_CHOICES)
    quantite = models.PositiveIntegerField()
    delai = models.DateTimeField()
    statut = models.CharField(max_length=20, choices=STATUT_DEMANDE_CHOICES, default='active')
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.groupe_sanguin} – {self.hopital.nom} ({self.quantite} poches)"


class ReponseAppel(models.Model):
    demande = models.ForeignKey(DemandeUrgente, on_delete=models.CASCADE, related_name='reponses')
    donneur = models.ForeignKey('comptes.Donneur', on_delete=models.CASCADE)
    date_reponse = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=20, choices=STATUT_REPONSE_CHOICES, default='en_attente')

    class Meta:
        unique_together = ('demande', 'donneur')