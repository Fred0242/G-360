from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from datetime import date
from clients.models import Client
from produits.models import Produit
from factures.models import Facture, LigneFacture

@login_required
def dashboard(request):
    aujourd_hui = date.today()

    # Stats principales
    total_clients = Client.objects.filter(actif=True).count()

    ventes_mois = Facture.objects.filter(
        date_emission__month=aujourd_hui.month,
        date_emission__year=aujourd_hui.year
    ).aggregate(s=Sum('montant_paye'))['s'] or 0

    total_produits = Produit.objects.filter(actif=True).count()

    dettes_total = Client.objects.filter(
        actif=True, solde_credit__gt=0
    ).aggregate(s=Sum('solde_credit'))['s'] or 0

    # Clients avec dettes (5 plus importants)
    clients_en_dette = Client.objects.filter(
        actif=True, solde_credit__gt=0
    ).order_by('-solde_credit')[:5]

    # Top produits vendus ce mois
    top_produits = LigneFacture.objects.filter(
        facture__date_emission__month=aujourd_hui.month,
        facture__date_emission__year=aujourd_hui.year
    ).values('produit__nom').annotate(
        total_vendu=Sum('quantite')
    ).order_by('-total_vendu')[:5]

    # Max pour la barre de progression
    max_vendu = top_produits[0]['total_vendu'] if top_produits else 1

    # Dernières factures
    dernieres_factures = Facture.objects.select_related('client').order_by('-date_emission')[:5]

    context = {
        'today': aujourd_hui.strftime('%A %d %B %Y'),
        'stats': {
            'clients': total_clients,
            'ventes_mois': f"{int(ventes_mois):,}".replace(',', ' '),
            'produits': total_produits,
            'dettes_total': f"{int(dettes_total):,}".replace(',', ' '),
        },
        'clients_en_dette': clients_en_dette,
        'top_produits': top_produits,
        'max_vendu': max_vendu,
        'dernieres_factures': dernieres_factures,
    }
    return render(request, 'dashboard/home.html', context)


@login_required
def historique(request):
    return render(request, 'dashboard/historique.html', {
        'today': date.today().strftime('%A %d %B %Y')
    })

@login_required
def support(request):
    return render(request, 'dashboard/support.html', {
        'today': date.today().strftime('%A %d %B %Y')
    })
