from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['nom', 'telephone', 'solde_credit', 'actif']
    search_fields = ['nom', 'telephone']
    list_filter = ['actif']
