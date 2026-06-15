from django.urls import path
from .views import (
    CreerReservationView,
    MesReservationsView,
    MesDemandesView,
    DetailReservationView,
    ConfirmerReservationView,
    AnnulerReservationView,
    LaisserAvisView,
    EnvoyerMessageView,
    EnvoyerPhotoView,
    MessagesReservationView,
    MarquerMessagesLusView,
    ModifierMessageView,
    SupprimerMessageView,
    PayerReservationView,
    ValiderCodeView,
    SignalerLitigeView,
)

urlpatterns = [

    # Réservations
    path('creer/',
         CreerReservationView.as_view(),
         name='creer-reservation'),

    path('mes-reservations/',
         MesReservationsView.as_view(),
         name='mes-reservations'),

    path('mes-demandes/',
         MesDemandesView.as_view(),
         name='mes-demandes'),

    path('<int:id_reservation>/',
         DetailReservationView.as_view(),
         name='detail-reservation'),

    path('<int:id_reservation>/confirmer/',
         ConfirmerReservationView.as_view(),
         name='confirmer-reservation'),

    path('<int:id_reservation>/annuler/',
         AnnulerReservationView.as_view(),
         name='annuler-reservation'),

    # Avis
    path('<int:id_reservation>/avis/',
         LaisserAvisView.as_view(),
         name='laisser-avis'),

    # ── Paiement séquestre ──
    path('<int:id_reservation>/payer/',
         PayerReservationView.as_view(),
         name='payer-reservation'),

    path('<int:id_reservation>/valider-code/',
         ValiderCodeView.as_view(),
         name='valider-code'),

    path('<int:id_reservation>/litige/',
         SignalerLitigeView.as_view(),
         name='signaler-litige'),

    # Messages
    path('messages/envoyer/',
         EnvoyerMessageView.as_view(),
         name='envoyer-message'),

    path('messages/photo/',
         EnvoyerPhotoView.as_view(),
         name='envoyer-photo'),

    path('<int:id_reservation>/messages/',
         MessagesReservationView.as_view(),
         name='messages-reservation'),

    path('<int:id_reservation>/messages/lus/',
         MarquerMessagesLusView.as_view(),
         name='marquer-messages-lus'),

    path('messages/<int:id_message>/modifier/',
         ModifierMessageView.as_view(),
         name='modifier-message'),

    path('messages/<int:id_message>/supprimer/',
         SupprimerMessageView.as_view(),
         name='supprimer-message'),
]