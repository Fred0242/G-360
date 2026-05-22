from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('stock/', views.stock, name='stock'),
    path('ventes/', views.ventes, name='ventes'),
    path('historique/', views.historique, name='historique'),
    path('support/', views.support, name='support'),
]
