from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Client
from datetime import date

@login_required
def clients_liste(request):
    clients = Client.objects.filter(actif=True)
    search = request.GET.get('search', '')
    vue = request.GET.get('vue', 'tous')

    if search:
        clients = clients.filter(nom__icontains=search) | clients.filter(telephone__icontains=search)

    if vue == 'dettes':
        clients = Client.objects.filter(actif=True, solde_credit__gt=0)
        if search:
            clients = clients.filter(nom__icontains=search) | clients.filter(telephone__icontains=search)

    total_dettes = sum(c.solde_credit for c in Client.objects.filter(actif=True, solde_credit__gt=0))

    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'clients': clients,
        'search': search,
        'vue': vue,
        'total_clients': Client.objects.filter(actif=True).count(),
        'clients_en_dette': Client.objects.filter(actif=True, solde_credit__gt=0).count(),
        'total_dettes': total_dettes,
    }
    return render(request, 'clients/liste.html', context)


@login_required
def client_fiche(request, pk):
    client = get_object_or_404(Client, id=pk)
    factures = client.factures.all().order_by('-date_emission')
    context = {
        'today': date.today().strftime('%A %d %B %Y'),
        'client': client,
        'factures': factures,
    }
    return render(request, 'clients/fiche.html', context)


@login_required
def client_ajouter(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        telephone = request.POST.get('telephone', '')
        adresse = request.POST.get('adresse', '')
        Client.objects.create(nom=nom, telephone=telephone, adresse=adresse)
        messages.success(request, f'Client "{nom}" ajouté avec succès.')
        return redirect('clients_liste')
    return render(request, 'clients/form.html', {
        'today': date.today().strftime('%A %d %B %Y'),
        'action': 'Ajouter',
    })


@login_required
def client_modifier(request, pk):
    client = get_object_or_404(Client, id=pk)
    if request.method == 'POST':
        client.nom = request.POST.get('nom')
        client.telephone = request.POST.get('telephone', '')
        client.adresse = request.POST.get('adresse', '')
        client.save()
        messages.success(request, f'Client "{client.nom}" modifié.')
        return redirect('clients_liste')
    return render(request, 'clients/form.html', {
        'today': date.today().strftime('%A %d %B %Y'),
        'client': client,
        'action': 'Modifier',
    })


@login_required
def client_supprimer(request, pk):
    client = get_object_or_404(Client, id=pk)
    client.actif = False
    client.save()
    messages.success(request, f'Client "{client.nom}" supprimé.')
    return redirect('clients_liste')
