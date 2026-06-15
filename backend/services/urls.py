from django.urls import path
from .views import (
    CategorieListView,
    MetierListView,
    MetierParCategorieView,
    CommuneListView,
    RecherchePrestatairesView,
    ServiceListCreateView,
    ServiceDetailView,
    MesServicesView,
)

urlpatterns = [

    # Catégories
    path('categories/',
         CategorieListView.as_view(),
         name='categories-list'),

    # Métiers
    path('metiers/',
         MetierListView.as_view(),
         name='metiers-list'),

    path('metiers/categorie/<int:id_categorie>/',
         MetierParCategorieView.as_view(),
         name='metiers-par-categorie'),

    # Communes
    path('communes/',
         CommuneListView.as_view(),
         name='communes-list'),

    # Recherche prestataires
    path('recherche/',
         RecherchePrestatairesView.as_view(),
         name='recherche-prestataires'),

    # Services — CRUD
    path('services/',
         ServiceListCreateView.as_view(),
         name='services-list-create'),

    path('services/<int:id_service>/',
         ServiceDetailView.as_view(),
         name='service-detail'),

    # Services du prestataire connecté
    path('mes-services/',
         MesServicesView.as_view(),
         name='mes-services'),
]