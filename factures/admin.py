from django.contrib import admin
from .models import Facture, LigneFacture, Paiement

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ['numero', 'nom_client_affiche', 'montant_total', 'montant_paye', 'statut']
    list_filter = ['statut', 'mode_paiement']
    search_fields = ['numero', 'client__nom']

admin.site.register(LigneFacture)
admin.site.register(Paiement)
