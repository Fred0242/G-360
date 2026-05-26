from django.urls import path
from . import views

urlpatterns = [
    path('', views.ventes_liste, name='ventes'),
    path('nouvelle/', views.nouvelle_vente, name='nouvelle_vente'),
    path('<uuid:pk>/', views.facture_detail, name='facture_detail'),
    path('<uuid:pk>/paiement/', views.enregistrer_paiement, name='enregistrer_paiement'),
    path('<uuid:pk>/pdf/', views.facture_pdf, name='facture_pdf'),
]
