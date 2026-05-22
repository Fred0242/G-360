from django.db import models
from clients.models import Client
from produits.models import Produit
import uuid

class Facture(models.Model):
    STATUT_CHOICES = [
        ('payee', 'Payée'),
        ('partielle', 'Partiellement payée'),
        ('impayee', 'Impayée'),
        ('credit', 'Crédit (à recouvrer)'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('cash', 'Cash'),
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
        ('credit', 'Crédit'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='factures'
    )
    client_nom_temp = models.CharField(max_length=100, blank=True)
    date_emission = models.DateTimeField(auto_now_add=True)
    date_echeance = models.DateField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='impayee')
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='cash')
    montant_total = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    montant_paye = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date_emission']
        verbose_name = 'Facture'
        verbose_name_plural = 'Factures'

    def __str__(self):
        return f"Facture {self.numero}"

    @property
    def montant_du(self):
        return self.montant_total - self.montant_paye

    @property
    def nom_client_affiche(self):
        if self.client:
            return self.client.nom
        return self.client_nom_temp or "Client anonyme"

    def generer_numero(self):
        from django.utils import timezone
        annee = timezone.now().year
        derniere = Facture.objects.filter(
            numero__startswith=f'G360-{annee}-'
        ).count()
        return f"G360-{annee}-{str(derniere + 1).zfill(4)}"

    def save(self, *args, **kwargs):
        if not self.numero:
            self.numero = self.generer_numero()
        if self.montant_paye >= self.montant_total and self.montant_total > 0:
            self.statut = 'payee'
        elif self.montant_paye > 0:
            self.statut = 'partielle'
        elif self.mode_paiement == 'credit':
            self.statut = 'credit'
        super().save(*args, **kwargs)


class LigneFacture(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(
        Facture, on_delete=models.CASCADE, related_name='lignes'
    )
    produit = models.ForeignKey(
        Produit, on_delete=models.PROTECT, related_name='lignes_facture'
    )
    quantite = models.IntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire


class Paiement(models.Model):
    MODE_CHOICES = [
        ('cash', 'Cash'),
        ('orange_money', 'Orange Money'),
        ('wave', 'Wave'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    facture = models.ForeignKey(
        Facture, on_delete=models.CASCADE, related_name='paiements'
    )
    montant = models.DecimalField(max_digits=12, decimal_places=0)
    mode_paiement = models.CharField(max_length=20, choices=MODE_CHOICES)
    date_paiement = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ['-date_paiement']

    def __str__(self):
        return f"{int(self.montant):,} FCFA — {self.mode_paiement}"
