from django.db import models

class Don(models.Model):
    donneur = models.ForeignKey('comptes.Donneur', on_delete=models.CASCADE, related_name='dons')
    hopital = models.ForeignKey('comptes.Hopital', on_delete=models.CASCADE, related_name='dons_recus')
    date_don = models.DateField()
    notes = models.TextField(blank=True)
    valide = models.BooleanField(default=False)

    def __str__(self):
        return f"Don de {self.donneur} le {self.date_don}"
