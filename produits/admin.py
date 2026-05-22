from django.contrib import admin
from .models import Categorie, Produit, MouvementStock

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom']

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'reference', 'categorie', 'prix_vente', 'quantite_stock']
    search_fields = ['nom', 'reference']
    list_filter = ['categorie', 'actif']

@admin.register(MouvementStock)
class MouvementAdmin(admin.ModelAdmin):
    list_display = ['produit', 'type_mouvement', 'quantite', 'date_mouvement']
