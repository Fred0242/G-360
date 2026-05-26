from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import date

@login_required
def dashboard(request):
    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'stats': {
            'clients': 0,
            # 'ventes_mois': 0,
            'produits': 0,
            'dettes_total': 0,
        }
    }
    return render(request, 'dashboard/home.html', context)

@login_required
def stock(request):
    return render(request, 'dashboard/stock.html', {'today': date.today().strftime('%A %d %B %Y')})

@login_required
def ventes(request):
    return render(request, 'dashboard/ventes.html', {'today': date.today().strftime('%A %d %B %Y')})

@login_required
def historique(request):
    return render(request, 'dashboard/historique.html', {'today': date.today().strftime('%A %d %B %Y')})

@login_required
def support(request):
    return render(request, 'dashboard/support.html', {'today': date.today().strftime('%A %d %B %Y')})
