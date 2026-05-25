
from django.urls import path
from . import views

urlpatterns = [
    path('', views.stock_liste, name='stock'),
    path('ajouter/', views.produit_ajouter, name='produit_ajouter'),
    path('modifier/<uuid:pk>/', views.produit_modifier, name='produit_modifier'),
    path('ajuster/<uuid:pk>/', views.ajuster_stock, name='ajuster_stock'),
    path('supprimer/<uuid:pk>/', views.produit_supprimer, name='produit_supprimer'),
]
