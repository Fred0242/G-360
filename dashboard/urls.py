from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # path('ventes/', views.ventes, name='ventes'),
    path('historique/', views.historique, name='historique'),
    path('support/', views.support, name='support'),
]
