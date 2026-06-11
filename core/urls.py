from django.contrib import admin
from django.urls import path, include
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('dashboard.urls')),
    path('stock/', include('produits.urls')),
    path('clients/', include('clients.urls')),
    path('ventes/', include('factures.urls')),
]
