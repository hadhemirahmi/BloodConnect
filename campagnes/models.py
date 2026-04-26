from django.db import models

class Campagne(models.Model):
    hopital = models.ForeignKey('comptes.Hopital', on_delete=models.CASCADE, related_name='campagnes')
    nom = models.CharField(max_length=200)
    date = models.DateField()
    lieu = models.CharField(max_length=255)
    groupes_cibles = models.CharField(max_length=100)
    capacite_par_creneau = models.PositiveIntegerField(default=10)
    nb_creneaux = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.nom

    @property
    def capacite_totale(self):
        return self.capacite_par_creneau * self.nb_creneaux


class Inscription(models.Model):
    campagne = models.ForeignKey(Campagne, on_delete=models.CASCADE, related_name='inscriptions')
    donneur = models.ForeignKey('comptes.Donneur', on_delete=models.CASCADE)
    creneau_index = models.PositiveIntegerField()  
    creneau_horaire = models.CharField(max_length=50) 
    date_inscription = models.DateTimeField(auto_now_add=True)
    present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('campagne', 'donneur')