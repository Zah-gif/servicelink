from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta
import uuid
from .models import Paiement, Abonnement
from .serializers import (
    PaiementSerializer,
    CreerPaiementSerializer,
    AbonnementSerializer,
    SouscrireAbonnementSerializer,
)
from users.models import Prestataire
from reservations.models import Reservation


# ──────────────────────────────────────────
#  CRÉER UN PAIEMENT
#  POST /api/payments/paiement/creer/
# ──────────────────────────────────────────
class CreerPaiementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreerPaiementSerializer(data=request.data)
        if serializer.is_valid():
            # Générer une référence unique CinetPay
            reference = f"SL-{uuid.uuid4().hex[:12].upper()}"

            paiement = serializer.save(
                reference_paiement=reference,
                statut_paiement='en_attente'
            )

            # Ici on intégrerait l'API CinetPay en production
            # Pour l'instant on simule une confirmation

            return Response({
                'message':   'Paiement initié avec succès !',
                'reference': reference,
                'paiement':  PaiementSerializer(paiement).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  CONFIRMER UN PAIEMENT (webhook CinetPay)
#  POST /api/payments/paiement/confirmer/
# ──────────────────────────────────────────
class ConfirmerPaiementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        reference = request.data.get('reference')
        if not reference:
            return Response(
                {'error': 'Référence de paiement obligatoire.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            paiement = Paiement.objects.get(reference_paiement=reference)
        except Paiement.DoesNotExist:
            return Response(
                {'error': 'Paiement introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        paiement.statut_paiement = 'confirme'
        paiement.save()

        # Mettre à jour le statut de la réservation
        reservation = paiement.id_reservation
        reservation.statut = 'en_cours'
        reservation.save()

        return Response({
            'message': 'Paiement confirmé !',
            'paiement': PaiementSerializer(paiement).data
        })


# ──────────────────────────────────────────
#  MES PAIEMENTS
#  GET /api/payments/mes-paiements/
# ──────────────────────────────────────────
class MesPaiementsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = PaiementSerializer

    def get_queryset(self):
        try:
            client = self.request.user.client
            return Paiement.objects.filter(
                id_reservation__id_client=client
            ).order_by('-date_paiement')
        except Exception:
            return Paiement.objects.none()


# ──────────────────────────────────────────
#  SOUSCRIRE UN ABONNEMENT PREMIUM
#  POST /api/payments/abonnement/souscrire/
# ──────────────────────────────────────────
class SouscrireAbonnementView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Vérifier que c'est un prestataire
        try:
            prestataire = request.user.prestataire
        except Prestataire.DoesNotExist:
            return Response(
                {'error': 'Seuls les prestataires peuvent souscrire un abonnement.'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SouscrireAbonnementSerializer(data=request.data)
        if serializer.is_valid():
            type_offre = serializer.validated_data['type_offre']

            # Définir les montants et durées
            if type_offre == 'mensuel':
                montant   = 5000
                duree     = 30
            else:  # annuel
                montant   = 50000
                duree     = 365

            date_debut = timezone.now().date()
            date_fin   = date_debut + timedelta(days=duree)

            # Désactiver l'ancien abonnement actif
            Abonnement.objects.filter(
                id_prestataire=prestataire,
                est_actif=True
            ).update(est_actif=False)

            # Créer le nouvel abonnement
            abonnement = Abonnement.objects.create(
                id_prestataire=prestataire,
                type_offre=type_offre,
                montant_paye=montant,
                date_debut=date_debut,
                date_fin=date_fin,
                est_actif=True
            )

            # Mettre à jour le prestataire
            prestataire.est_premium      = True
            prestataire.date_fin_premium = date_fin
            prestataire.save()

            return Response({
                'message':     f'Abonnement {type_offre} activé avec succès !',
                'abonnement':  AbonnementSerializer(abonnement).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  MON ABONNEMENT ACTUEL
#  GET /api/payments/abonnement/mon-abonnement/
# ──────────────────────────────────────────
class MonAbonnementView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            prestataire = request.user.prestataire
        except Prestataire.DoesNotExist:
            return Response(
                {'error': 'Profil prestataire introuvable.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            abonnement = Abonnement.objects.get(
                id_prestataire=prestataire,
                est_actif=True
            )
            return Response(AbonnementSerializer(abonnement).data)
        except Abonnement.DoesNotExist:
            return Response({
                'message':    'Aucun abonnement actif.',
                'est_premium': False
            })