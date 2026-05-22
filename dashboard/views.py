from django.shortcuts import render

def dashboard(request):
    context = {
        'app_name': 'G-360',
        'user_name': 'Franchir',
        'stats': {
            'clients': 0,
            'factures': 0,
            'produits': 0,
        }
    }
    return render(request, 'dashboard/home.html', context)
