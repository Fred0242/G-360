from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Client
from datetime import date

@login_required
def clients_liste(request):
    clients = Client.objects.all()
    clients_en_dette = Client.objects.filter(solde_credit__gt=0)
    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'clients': clients,
        'clients_en_dette': clients_en_dette,
    }
    return render(request, 'clients/liste.html', context)
