from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, Categorie, MouvementStock
from datetime import date

@login_required
def stock_liste(request):
    produits = Produit.objects.select_related('categorie').filter(actif=True)
    categories = Categorie.objects.all()

    # Filtres
    search = request.GET.get('search', '')
    categorie_id = request.GET.get('categorie', '')
    filtre_stock = request.GET.get('stock', '')

    if search:
        produits = produits.filter(nom__icontains=search)
    if categorie_id:
        produits = produits.filter(categorie__id=categorie_id)
    if filtre_stock == 'ok':
        produits = produits.filter(quantite_stock__gt=5)
    elif filtre_stock == 'faible':
        produits = produits.filter(quantite_stock__gt=0, quantite_stock__lte=5)
    elif filtre_stock == 'rupture':
        produits = produits.filter(quantite_stock=0)

    # Stats résumé
    tous = Produit.objects.filter(actif=True)
    stats = {
        'total': tous.count(),
        'en_stock': tous.filter(quantite_stock__gt=5).count(),
        'faible': tous.filter(quantite_stock__gt=0, quantite_stock__lte=5).count(),
        'rupture': tous.filter(quantite_stock=0).count(),
    }

    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'produits': produits,
        'categories': categories,
        'stats': stats,
        'search': search,
        'categorie_id': categorie_id,
        'filtre_stock': filtre_stock,
    }
    return render(request, 'produits/stock.html', context)


@login_required
def produit_ajouter(request):
    categories = Categorie.objects.all()
    if request.method == 'POST':
        nom = request.POST.get('nom')
        reference = request.POST.get('reference') or None
        categorie_id = request.POST.get('categorie')
        prix_achat = request.POST.get('prix_achat', 0)
        prix_vente = request.POST.get('prix_vente')
        quantite = int(request.POST.get('quantite_stock', 0))
        seuil = request.POST.get('seuil_alerte', 5)
        description = request.POST.get('description', '')

        categorie = None
        if categorie_id:
            categorie = get_object_or_404(Categorie, id=categorie_id)

        produit = Produit.objects.create(
            nom=nom,
            reference=reference,
            categorie=categorie,
            prix_achat=prix_achat,
            prix_vente=prix_vente,
            quantite_stock=quantite,
            seuil_alerte=seuil,
            description=description,
        )

        # Enregistre le mouvement initial
        if quantite > 0:
            MouvementStock.objects.create(
                produit=produit,
                type_mouvement='entree',
                quantite=quantite,
                quantite_avant=0,
                quantite_apres=quantite,
                motif='Stock initial'
            )

        messages.success(request, f'Produit "{nom}" ajouté avec succès.')
        return redirect('stock')

    return render(request, 'produits/produit_form.html', {
        'categories': categories,
        'today': date.today().strftime('%A %d %B %Y'),
        'action': 'Ajouter',
    })


@login_required
def produit_modifier(request, pk):
    produit = get_object_or_404(Produit, id=pk)
    categories = Categorie.objects.all()

    if request.method == 'POST':
        produit.nom = request.POST.get('nom')
        produit.reference = request.POST.get('reference') or None
        categorie_id = request.POST.get('categorie')
        produit.prix_achat = request.POST.get('prix_achat', 0)
        produit.prix_vente = request.POST.get('prix_vente')
        produit.seuil_alerte = request.POST.get('seuil_alerte', 5)
        produit.description = request.POST.get('description', '')
        produit.categorie = get_object_or_404(Categorie, id=categorie_id) if categorie_id else None
        produit.save()
        messages.success(request, f'Produit "{produit.nom}" modifié.')
        return redirect('stock')

    return render(request, 'produits/produit_form.html', {
        'produit': produit,
        'categories': categories,
        'today': date.today().strftime('%A %d %B %Y'),
        'action': 'Modifier',
    })


@login_required
def ajuster_stock(request, pk):
    produit = get_object_or_404(Produit, id=pk)

    if request.method == 'POST':
        type_mouvement = request.POST.get('type_mouvement')
        quantite = int(request.POST.get('quantite', 0))
        motif = request.POST.get('motif', '')

        avant = produit.quantite_stock

        if type_mouvement == 'entree':
            produit.quantite_stock += quantite
        elif type_mouvement == 'sortie':
            if quantite > produit.quantite_stock:
                messages.error(request, 'Quantité insuffisante en stock.')
                return redirect('stock')
            produit.quantite_stock -= quantite
        elif type_mouvement == 'ajustement':
            produit.quantite_stock = quantite

        produit.save()

        MouvementStock.objects.create(
            produit=produit,
            type_mouvement=type_mouvement,
            quantite=quantite,
            quantite_avant=avant,
            quantite_apres=produit.quantite_stock,
            motif=motif
        )

        messages.success(request, f'Stock de "{produit.nom}" mis à jour.')
        return redirect('stock')

    return render(request, 'produits/ajuster_stock.html', {
        'produit': produit,
        'today': date.today().strftime('%A %d %B %Y'),
    })


@login_required
def produit_supprimer(request, pk):
    produit = get_object_or_404(Produit, id=pk)
    produit.actif = False
    produit.save()
    messages.success(request, f'Produit "{produit.nom}" supprimé.')
    return redirect('stock')
