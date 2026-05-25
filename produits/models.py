from django.db import models
import uuid

class Categorie(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


class Produit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    categorie = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='produits'
    )
    nom = models.CharField(max_length=200)
    reference = models.CharField(max_length=50, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    prix_achat = models.DecimalField(max_digits=12, decimal_places=0, default=0)
    prix_vente = models.DecimalField(max_digits=12, decimal_places=0)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=5)
    actif = models.BooleanField(default=True)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nom']
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'

    def __str__(self):
        return self.nom

    @property
    def en_rupture(self):
        return self.quantite_stock == 0

    @property
    def stock_faible(self):
        return 0 < self.quantite_stock <= self.seuil_alerte

    @property
    def marge(self):
        return self.prix_vente - self.prix_achat

    @property
    def prix_formate(self):
        return f"{int(self.prix_vente):,} FCFA".replace(',', ' ')


class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    produit = models.ForeignKey(
        Produit, on_delete=models.CASCADE, related_name='mouvements'
    )
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    quantite_avant = models.IntegerField()
    quantite_apres = models.IntegerField()
    motif = models.CharField(max_length=200, blank=True)
    date_mouvement = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_mouvement']

    def __str__(self):
        return f"{self.produit.nom} — {self.type_mouvement} {self.quantite}"
