from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Categorie, Metier, Commune, Service
from .serializers import (
    CategorieSerializer,
    MetierSerializer,
    CommuneSerializer,
    ServiceSerializer,
    PrestataireRechercheSerializer,
)
from users.models import Prestataire


# ──────────────────────────────────────────
#  LISTE DES CATÉGORIES
# ──────────────────────────────────────────
class CategorieListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = CategorieSerializer
    queryset           = Categorie.objects.filter(est_active=True).order_by('nom_categorie')


# ──────────────────────────────────────────
#  LISTE DES MÉTIERS
# ──────────────────────────────────────────
class MetierListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = MetierSerializer
    queryset           = Metier.objects.filter(est_actif=True).order_by('nom_metier')


# ──────────────────────────────────────────
#  MÉTIERS PAR CATÉGORIE
# ──────────────────────────────────────────
class MetierParCategorieView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = MetierSerializer

    def get_queryset(self):
        id_categorie = self.kwargs['id_categorie']
        return Metier.objects.filter(
            id_categorie=id_categorie,
            est_actif=True
        ).order_by('nom_metier')


# ──────────────────────────────────────────
#  LISTE DES COMMUNES
# ──────────────────────────────────────────
class CommuneListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class   = CommuneSerializer
    queryset           = Commune.objects.all().order_by('nom_commune')


# ──────────────────────────────────────────
#  LISTE & CRÉATION DE SERVICES
#  GET  /api/services/services/
#  POST /api/services/services/
# ──────────────────────────────────────────
class ServiceListCreateView(generics.ListCreateAPIView):
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        queryset = Service.objects.filter(est_actif=True)

        # Filtre par catégorie
        id_categorie = self.request.query_params.get('categorie')
        if id_categorie:
            queryset = queryset.filter(id_categorie=id_categorie)

        # Filtre par métier
        id_metier = self.request.query_params.get('metier')
        if id_metier:
            queryset = queryset.filter(id_metier=id_metier)

        # Filtre par prestataire
        id_prestataire = self.request.query_params.get('prestataire')
        if id_prestataire:
            queryset = queryset.filter(id_prestataire=id_prestataire)

        return queryset.order_by('-date_creation')

    def perform_create(self, serializer):
        # Associer automatiquement le prestataire connecté
        prestataire = self.request.user.prestataire
        serializer.save(id_prestataire=prestataire)


# ──────────────────────────────────────────
#  DÉTAIL, MODIFICATION & SUPPRESSION SERVICE
#  GET    /api/services/services/<id>/
#  PUT    /api/services/services/<id>/
#  DELETE /api/services/services/<id>/
# ──────────────────────────────────────────
class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class   = ServiceSerializer
    lookup_field       = 'id_service'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Service.objects.all()

    def destroy(self, request, *args, **kwargs):
        # Désactiver au lieu de supprimer
        service = self.get_object()
        service.est_actif = False
        service.save()
        return Response(
            {'message': 'Service désactivé avec succès.'},
            status=status.HTTP_200_OK
        )


# ──────────────────────────────────────────
#  SERVICES D'UN PRESTATAIRE
#  GET /api/services/mes-services/
# ──────────────────────────────────────────
class MesServicesView(generics.ListAPIView):
    serializer_class   = ServiceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        prestataire = self.request.user.prestataire
        return Service.objects.filter(
            id_prestataire=prestataire
        ).order_by('-date_creation')


# ──────────────────────────────────────────
#  RECHERCHE DE PRESTATAIRES
#  GET /api/services/recherche/?commune=1&categorie=2&metier=3
# ──────────────────────────────────────────
class RecherchePrestatairesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = Prestataire.objects.filter(
            est_actif=True,
            est_disponible=True
        )

        # Filtre par commune — via la table intervient_dans
        id_commune = request.query_params.get('commune')
        if id_commune:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT id_prestataire FROM intervient_dans WHERE id_commune = %s",
                    [id_commune]
                )
                ids = [row[0] for row in cursor.fetchall()]
            queryset = queryset.filter(id_prestataire__in=ids)

        # Filtre par catégorie — via les services
        id_categorie = request.query_params.get('categorie')
        if id_categorie:
            queryset = queryset.filter(
                services__id_categorie=id_categorie,
                services__est_actif=True
            ).distinct()

        # Filtre par métier — via les services
        id_metier = request.query_params.get('metier')
        if id_metier:
            queryset = queryset.filter(
                services__id_metier=id_metier,
                services__est_actif=True
            ).distinct()

        # Filtre par note minimale
        note_min = request.query_params.get('note')
        if note_min:
            queryset = queryset.filter(note_moyenne__gte=note_min)

        # Filtre premium uniquement
        premium = request.query_params.get('premium')
        if premium == 'true':
            queryset = queryset.filter(est_premium=True)

        # Premium en premier puis meilleure note
        queryset = queryset.order_by('-est_premium', '-note_moyenne')

        serializer = PrestataireRechercheSerializer(queryset, many=True)
        return Response({
            'count':   queryset.count(),
            'results': serializer.data
        })