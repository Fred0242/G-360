from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db.models import Sum, Count
from .models import Facture, LigneFacture, Paiement
from clients.models import Client
from produits.models import Produit, MouvementStock
from datetime import date, datetime, timedelta

@login_required
def ventes_liste(request):
    factures = Facture.objects.select_related('client').all()

    # Filtres temporels
    filtre = request.GET.get('filtre', 'mois')
    date_custom = request.GET.get('date_custom', '')
    aujourd_hui = date.today()

    if filtre == 'jour':
        factures = factures.filter(date_emission__date=aujourd_hui)
    elif filtre == 'semaine':
        debut = aujourd_hui - timedelta(days=aujourd_hui.weekday())
        factures = factures.filter(date_emission__date__gte=debut)
    elif filtre == 'mois':
        factures = factures.filter(
            date_emission__month=aujourd_hui.month,
            date_emission__year=aujourd_hui.year
        )
    elif filtre == 'annee':
        factures = factures.filter(date_emission__year=aujourd_hui.year)
    elif filtre == 'custom' and date_custom:
        factures = factures.filter(date_emission__date=date_custom)

    # Stats
    total_encaisse = factures.aggregate(s=Sum('montant_paye'))['s'] or 0
    total_attente = factures.aggregate(s=Sum('montant_total'))['s'] or 0
    total_attente -= total_encaisse

    # Top produit du mois
    from django.db.models import F
    top_produit = LigneFacture.objects.filter(
        facture__date_emission__month=aujourd_hui.month,
        facture__date_emission__year=aujourd_hui.year
    ).values('produit__nom').annotate(
        total_vendu=Sum('quantite')
    ).order_by('-total_vendu').first()

    context = {
        'today': aujourd_hui.strftime('%A %d %B %Y'),
        'factures': factures.order_by('-date_emission'),
        'filtre': filtre,
        'date_custom': date_custom,
        'stats': {
            'total_factures': factures.count(),
            'total_encaisse': total_encaisse,
            'total_attente': total_attente,
            'top_produit': top_produit['produit__nom'] if top_produit else '—',
        }
    }
    return render(request, 'factures/liste.html', context)


@login_required
def nouvelle_vente(request):
    clients = Client.objects.filter(actif=True)
    produits = Produit.objects.filter(actif=True, quantite_stock__gt=0)

    if request.method == 'POST':
        # Récupère les données
        client_id = request.POST.get('client_id') or None
        client_nom_temp = request.POST.get('client_nom_temp', '')
        mode_paiement = request.POST.get('mode_paiement', 'cash')
        notes = request.POST.get('notes', '')
        date_echeance = request.POST.get('date_echeance') or None

        # Lignes de produits
        produit_ids = request.POST.getlist('produit_id[]')
        quantites = request.POST.getlist('quantite[]')
        prix_unitaires = request.POST.getlist('prix_unitaire[]')

        if not produit_ids:
            messages.error(request, 'Ajoutez au moins un produit.')
            return redirect('nouvelle_vente')

        # Crée la facture
        client = Client.objects.get(id=client_id) if client_id else None
        facture = Facture(
            client=client,
            client_nom_temp=client_nom_temp,
            mode_paiement=mode_paiement,
            notes=notes,
            date_echeance=date_echeance,
        )
        facture.numero = facture.generer_numero()

        # Calcule le total
        montant_total = 0
        lignes_data = []
        for pid, qte, pu in zip(produit_ids, quantites, prix_unitaires):
            produit = Produit.objects.get(id=pid)
            qte = int(qte)
            pu = int(pu)
            sous_total = qte * pu
            montant_total += sous_total
            lignes_data.append((produit, qte, pu))

        facture.montant_total = montant_total

        # Si cash/wave/orange_money → payé immédiatement
        if mode_paiement in ['cash', 'orange_money', 'wave']:
            facture.montant_paye = montant_total
            facture.statut = 'payee'
        else:
            facture.montant_paye = 0
            facture.statut = 'credit'

        facture.save()

        # Crée les lignes et met à jour le stock
        for produit, qte, pu in lignes_data:
            LigneFacture.objects.create(
                facture=facture,
                produit=produit,
                quantite=qte,
                prix_unitaire=pu,
            )
            avant = produit.quantite_stock
            produit.quantite_stock -= qte
            produit.save()
            MouvementStock.objects.create(
                produit=produit,
                type_mouvement='sortie',
                quantite=qte,
                quantite_avant=avant,
                quantite_apres=produit.quantite_stock,
                motif=f'Vente — Facture {facture.numero}'
            )

        # Si crédit → met à jour la dette du client
        if mode_paiement == 'credit' and client:
            client.solde_credit += montant_total
            client.save()

        # Si cash → enregistre le paiement
        if mode_paiement in ['cash', 'orange_money', 'wave']:
            Paiement.objects.create(
                facture=facture,
                montant=montant_total,
                mode_paiement=mode_paiement,
            )

        messages.success(request, f'Facture {facture.numero} créée avec succès.')
        return redirect('facture_detail', pk=facture.id)

    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'clients': clients,
        'produits': produits,
    }
    return render(request, 'factures/nouvelle_vente.html', context)


@login_required
def facture_detail(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'facture': facture,
    }
    return render(request, 'factures/detail.html', context)


@login_required
def enregistrer_paiement(request, pk):
    facture = get_object_or_404(Facture, id=pk)

    if request.method == 'POST':
        montant = int(request.POST.get('montant', 0))
        mode = request.POST.get('mode_paiement', 'cash')

        if montant <= 0:
            messages.error(request, 'Montant invalide.')
            return redirect('facture_detail', pk=pk)

        if montant > facture.montant_du:
            messages.error(request, f'Montant supérieur au reste dû ({int(facture.montant_du):,} FCFA).')
            return redirect('facture_detail', pk=pk)

        Paiement.objects.create(
            facture=facture,
            montant=montant,
            mode_paiement=mode,
        )

        facture.montant_paye += montant

        # Met à jour la dette client
        if facture.client:
            facture.client.solde_credit -= montant
            if facture.client.solde_credit < 0:
                facture.client.solde_credit = 0
            facture.client.save()

        facture.save()
        messages.success(request, f'Paiement de {montant:,} FCFA enregistré.')
        return redirect('facture_detail', pk=pk)

    return render(request, 'factures/paiement.html', {
        'today': date.today().strftime('%A %d %B %Y'),
        'facture': facture,
    })


@login_required
def facture_pdf(request, pk):
    facture = get_object_or_404(Facture, id=pk)
    html = render_to_string('factures/pdf.html', {'facture': facture})
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'filename="facture-{facture.numero}.pdf"'
        return response
    except Exception as e:
        messages.error(request, f'Erreur PDF : {e}')
        return redirect('facture_detail', pk=pk)
