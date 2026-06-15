from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    InscriptionClientView,
    InscriptionPrestataireView,
    ConnexionView,
    DeconnexionView,
    ProfilView,
    ProfilPrestatairePublicView,
    ChangerMotDePasseView,
    UploadPhotoProfilView,
    ToggleFavoriView,
    MesFavorisView,
    ContactView,
)

urlpatterns = [

    # Inscription
    path('inscription/client/',
         InscriptionClientView.as_view(),
         name='inscription-client'),

    path('inscription/prestataire/',
         InscriptionPrestataireView.as_view(),
         name='inscription-prestataire'),

    # Authentification
    path('connexion/',
         ConnexionView.as_view(),
         name='connexion'),

    path('deconnexion/',
         DeconnexionView.as_view(),
         name='deconnexion'),

    path('token/refresh/',
         TokenRefreshView.as_view(),
         name='token-refresh'),

    # Profil
    path('profil/',
         ProfilView.as_view(),
         name='profil'),

    # Profil public prestataire
    path('prestataire/<int:id_prestataire>/',
         ProfilPrestatairePublicView.as_view(),
         name='profil-prestataire-public'),

    # Upload photo de profil prestataire
    path('prestataire/photo/',
         UploadPhotoProfilView.as_view(),
         name='upload-photo-profil'),

    # Favoris
    path('favoris/',
         MesFavorisView.as_view(),
         name='mes-favoris'),

    path('favoris/<int:id_prestataire>/',
         ToggleFavoriView.as_view(),
         name='toggle-favori'),

    # Sécurité
    path('changer-mot-de-passe/',
         ChangerMotDePasseView.as_view(),
         name='changer-mot-de-passe'),

    # Contact (public)
    path('contact/',
         ContactView.as_view(),
         name='contact'),
]