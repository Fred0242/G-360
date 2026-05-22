from django.urls import path
from . import views

urlpatterns = [
    path('', views.clients_liste, name='clients_liste'),
]
