from django.urls import path
from .views import (
    CreerPaiementView,
    ConfirmerPaiementView,
    MesPaiementsView,
    SouscrireAbonnementView,
    MonAbonnementView,
)

urlpatterns = [

    # Paiements
    path('paiement/creer/',
         CreerPaiementView.as_view(),
         name='creer-paiement'),

    path('paiement/confirmer/',
         ConfirmerPaiementView.as_view(),
         name='confirmer-paiement'),

    path('mes-paiements/',
         MesPaiementsView.as_view(),
         name='mes-paiements'),

    # Abonnements
    path('abonnement/souscrire/',
         SouscrireAbonnementView.as_view(),
         name='souscrire-abonnement'),

    path('abonnement/mon-abonnement/',
         MonAbonnementView.as_view(),
         name='mon-abonnement'),
]