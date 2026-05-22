from django.db import models
import uuid

class Client(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.CharField(max_length=200, blank=True)
    solde_credit = models.DecimalField(
        max_digits=12, decimal_places=0, default=0
    )
    date_inscription = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return self.nom

    @property
    def a_une_dette(self):
        return self.solde_credit > 0

    @property
    def solde_formate(self):
        return f"{int(self.solde_credit):,} FCFA".replace(',', ' ')
