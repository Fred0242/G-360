from django.urls import path
from . import views

urlpatterns = [
    path('', views.clients_liste, name='clients_liste'),
    path('ajouter/', views.client_ajouter, name='client_ajouter'),
    path('<uuid:pk>/', views.client_fiche, name='client_fiche'),
    path('<uuid:pk>/modifier/', views.client_modifier, name='client_modifier'),
    path('<uuid:pk>/supprimer/', views.client_supprimer, name='client_supprimer'),
]
