from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from datetime import date, timedelta
from clients.models import Client
from produits.models import Produit, MouvementStock
from factures.models import Facture, LigneFacture, Paiement

@login_required
def dashboard(request):
    aujourd_hui = date.today()

    total_clients = Client.objects.filter(actif=True).count()
    ventes_mois = Facture.objects.filter(
        date_emission__month=aujourd_hui.month,
        date_emission__year=aujourd_hui.year
    ).aggregate(s=Sum('montant_paye'))['s'] or 0
    total_produits = Produit.objects.filter(actif=True).count()
    dettes_total = Client.objects.filter(
        actif=True, solde_credit__gt=0
    ).aggregate(s=Sum('solde_credit'))['s'] or 0

    clients_en_dette = Client.objects.filter(
        actif=True, solde_credit__gt=0
    ).order_by('-solde_credit')[:5]

    top_produits = LigneFacture.objects.filter(
        facture__date_emission__month=aujourd_hui.month,
        facture__date_emission__year=aujourd_hui.year
    ).values('produit__nom').annotate(
        total_vendu=Sum('quantite')
    ).order_by('-total_vendu')[:5]

    max_vendu = top_produits[0]['total_vendu'] if top_produits else 1
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
    aujourd_hui = date.today()
    filtre = request.GET.get('filtre', 'mois')
    type_filtre = request.GET.get('type', 'tous')

    mouvements = MouvementStock.objects.select_related('produit').all()
    paiements = Paiement.objects.select_related('facture__client').all()

    if filtre == 'jour':
        mouvements = mouvements.filter(date_mouvement__date=aujourd_hui)
        paiements = paiements.filter(date_paiement__date=aujourd_hui)
    elif filtre == 'semaine':
        debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        mouvements = mouvements.filter(date_mouvement__date__gte=debut)
        paiements = paiements.filter(date_paiement__date__gte=debut)
    elif filtre == 'mois':
        mouvements = mouvements.filter(
            date_mouvement__month=aujourd_hui.month,
            date_mouvement__year=aujourd_hui.year
        )
        paiements = paiements.filter(
            date_paiement__month=aujourd_hui.month,
            date_paiement__year=aujourd_hui.year
        )
    elif filtre == 'annee':
        mouvements = mouvements.filter(date_mouvement__year=aujourd_hui.year)
        paiements = paiements.filter(date_paiement__year=aujourd_hui.year)

    if type_filtre == 'entree':
        mouvements = mouvements.filter(type_mouvement='entree')
    elif type_filtre == 'sortie':
        mouvements = mouvements.filter(type_mouvement='sortie')

    context = {
        'today': aujourd_hui.strftime('%A %d %B %Y'),
        'filtre': filtre,
        'type_filtre': type_filtre,
        'mouvements': mouvements.order_by('-date_mouvement')[:50],
        'paiements': paiements.order_by('-date_paiement')[:50],
        'stats': {
            'total_entrees': MouvementStock.objects.filter(type_mouvement='entree').count(),
            'total_sorties': MouvementStock.objects.filter(type_mouvement='sortie').count(),
            'total_paiements': Paiement.objects.aggregate(s=Sum('montant'))['s'] or 0,
        }
    }
    return render(request, 'dashboard/historique.html', context)


@login_required
def support(request):
    return render(request, 'dashboard/support.html', {
        'today': date.today().strftime('%A %d %B %Y')
    })
