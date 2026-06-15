from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from .models import Reservation, Avis, Message
from .serializers import (
    ReservationSerializer,
    CreerReservationSerializer,
    AvisSerializer,
    MessageSerializer,
    EnvoyerMessageSerializer,
    EnvoyerPhotoSerializer,
    ModifierMessageSerializer,
)
from users.models import Client, Prestataire


# ──────────────────────────────────────────
#  CRÉER UNE RÉSERVATION
# ──────────────────────────────────────────
class CreerReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response({'error': 'Seuls les clients peuvent faire des réservations.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CreerReservationSerializer(data=request.data)
        if serializer.is_valid():
            # Toujours créer en attente — le prestataire confirme et fixe le montant
            reservation = serializer.save(id_client=client, statut='en_attente')
            return Response({
                'message': 'Réservation créée avec succès !',
                'reservation': ReservationSerializer(reservation).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  MES RÉSERVATIONS (CLIENT)
# ──────────────────────────────────────────
class MesReservationsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ReservationSerializer

    def get_queryset(self):
        try:
            client = self.request.user.client
            return Reservation.objects.filter(id_client=client).order_by('-date_creation')
        except Client.DoesNotExist:
            return Reservation.objects.none()


# ──────────────────────────────────────────
#  MES DEMANDES (PRESTATAIRE)
# ──────────────────────────────────────────
class MesDemandesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = ReservationSerializer

    def get_queryset(self):
        try:
            prestataire = self.request.user.prestataire
            return Reservation.objects.filter(id_prestataire=prestataire).order_by('-date_creation')
        except Prestataire.DoesNotExist:
            return Reservation.objects.none()


# ──────────────────────────────────────────
#  DÉTAIL D'UNE RÉSERVATION
# ──────────────────────────────────────────
class DetailReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, id_reservation):
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        user            = request.user
        est_client      = hasattr(user, 'client')      and reservation.id_client == user.client
        est_prestataire = hasattr(user, 'prestataire') and reservation.id_prestataire == user.prestataire
        if not (est_client or est_prestataire):
            return Response({'error': 'Accès non autorisé.'}, status=status.HTTP_403_FORBIDDEN)
        return Response(ReservationSerializer(reservation).data)


# ──────────────────────────────────────────
#  CONFIRMER UNE RÉSERVATION + FIXER MONTANT
#  POST /api/reservations/<id>/confirmer/
#  Body: { "montant": 15000 }
# ──────────────────────────────────────────
class ConfirmerReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            prestataire = request.user.prestataire
        except Prestataire.DoesNotExist:
            return Response(
                {'error': 'Seuls les prestataires peuvent confirmer.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            reservation = Reservation.objects.get(
                id_reservation=id_reservation,
                id_prestataire=prestataire
            )
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        if reservation.statut != 'en_attente':
            return Response(
                {'error': 'Cette réservation ne peut plus être confirmée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Récupérer le montant proposé par le prestataire
        montant = request.data.get('montant')
        if not montant:
            return Response(
                {'error': 'Le montant est obligatoire pour confirmer.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            montant = float(montant)
            if montant <= 0:
                raise ValueError()
        except (ValueError, TypeError):
            return Response(
                {'error': 'Le montant doit être un nombre positif.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Passer au statut paiement_requis — client doit payer
        reservation.statut            = 'paiement_requis'
        reservation.montant           = montant
        reservation.date_confirmation = timezone.now()
        reservation.save()

        return Response({
            'message': f'Réservation confirmée ! Le client doit payer {int(montant):,} FCFA.',
            'reservation': ReservationSerializer(reservation).data,
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  ANNULER UNE RÉSERVATION
# ──────────────────────────────────────────
class AnnulerReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        user            = request.user
        est_client      = hasattr(user, 'client')      and reservation.id_client == user.client
        est_prestataire = hasattr(user, 'prestataire') and reservation.id_prestataire == user.prestataire
        if not (est_client or est_prestataire):
            return Response(
                {'error': "Vous n'êtes pas autorisé à annuler cette réservation."},
                status=status.HTTP_403_FORBIDDEN
            )

        if reservation.statut in ['terminee', 'annulee']:
            return Response(
                {'error': 'Cette réservation ne peut plus être annulée.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remboursement automatique si paiement déjà bloqué
        if reservation.statut_paiement == 'bloque':
            reservation.statut_paiement = 'rembourse'

        reservation.statut = 'annulee'
        reservation.save()
        return Response({'message': 'Réservation annulée.'})


# ──────────────────────────────────────────
#  LAISSER UN AVIS
# ──────────────────────────────────────────
class LaisserAvisView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response(
                {'error': 'Seuls les clients peuvent laisser un avis.'},
                status=status.HTTP_403_FORBIDDEN
            )
        try:
            reservation = Reservation.objects.get(
                id_reservation=id_reservation,
                id_client=client,
                statut='terminee'
            )
        except Reservation.DoesNotExist:
            return Response(
                {'error': 'Réservation introuvable ou non terminée.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if hasattr(reservation, 'avis'):
            return Response(
                {'error': 'Vous avez déjà laissé un avis pour cette réservation.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvisSerializer(data=request.data)
        if serializer.is_valid():
            avis        = serializer.save(id_reservation=reservation)
            prestataire = reservation.id_prestataire
            tous_avis   = Avis.objects.filter(id_reservation__id_prestataire=prestataire)
            prestataire.nombre_avis  = tous_avis.count()
            prestataire.note_moyenne = sum(a.note for a in tous_avis) / tous_avis.count()
            if prestataire.nombre_avis >= 20 and prestataire.note_moyenne >= 4.5:
                prestataire.badge_top = True
            prestataire.save()
            return Response(
                {'message': 'Avis enregistré !', 'avis': AvisSerializer(avis).data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  PAYER UNE RÉSERVATION (SIMULATION)
#  POST /api/reservations/<id>/payer/
#  — Client paie après que le prestataire a fixé le montant
# ──────────────────────────────────────────
class PayerReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response(
                {'error': 'Seuls les clients peuvent payer.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            reservation = Reservation.objects.get(
                id_reservation=id_reservation,
                id_client=client,
                statut='paiement_requis',        # ← statut correct
                statut_paiement='non_paye'
            )
        except Reservation.DoesNotExist:
            return Response(
                {'error': 'Réservation introuvable ou paiement déjà effectué.'},
                status=status.HTTP_404_NOT_FOUND
            )

        mode_paiement      = request.data.get('mode_paiement')
        telephone_paiement = request.data.get('telephone_paiement')

        if not mode_paiement:
            return Response({'error': 'Le mode de paiement est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)
        if not telephone_paiement:
            return Response({'error': 'Le numéro de téléphone est obligatoire.'}, status=status.HTTP_400_BAD_REQUEST)

        # Enregistrer le paiement — montant déjà fixé par le prestataire
        reservation.mode_paiement      = mode_paiement
        reservation.telephone_paiement = telephone_paiement
        reservation.statut_paiement    = 'bloque'
        reservation.statut             = 'confirmee'   # ← paiement reçu, prestataire peut intervenir
        reservation.date_paiement      = timezone.now()

        reservation.calculer_commission()
        code = reservation.generer_code_validation()
        reservation.save()

        return Response({
            'message':             'Paiement sécurisé ! Le prestataire peut intervenir.',
            'code_validation':     code,
            'montant':             str(reservation.montant),
            'montant_commission':  str(reservation.montant_commission),
            'montant_prestataire': str(reservation.montant_prestataire),
            'mode_paiement':       mode_paiement,
            'statut_paiement':     'bloque',
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  VALIDER LE CODE (PRESTATAIRE)
#  POST /api/reservations/<id>/valider-code/
#  — Termine automatiquement la réservation
# ──────────────────────────────────────────
class ValiderCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            prestataire = request.user.prestataire
        except Prestataire.DoesNotExist:
            return Response(
                {'error': 'Seuls les prestataires peuvent valider le code.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            reservation = Reservation.objects.get(
                id_reservation=id_reservation,
                id_prestataire=prestataire,
                statut_paiement='bloque'
            )
        except Reservation.DoesNotExist:
            return Response(
                {'error': 'Réservation introuvable ou paiement non bloqué.'},
                status=status.HTTP_404_NOT_FOUND
            )

        code_saisi = request.data.get('code_validation', '').strip().upper()

        if not code_saisi:
            return Response(
                {'error': 'Le code de validation est obligatoire.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if code_saisi != reservation.code_validation:
            return Response(
                {'error': 'Code incorrect. Demandez le bon code au client.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Libérer le paiement + terminer automatiquement
        reservation.statut_paiement = 'libere'
        reservation.date_liberation = timezone.now()
        reservation.statut          = 'terminee'   # ← terminée automatiquement
        reservation.save()

        return Response({
            'message':         'Code validé ! Paiement libéré. Réservation terminée.',
            'montant_recu':    str(reservation.montant_prestataire),
            'commission':      str(reservation.montant_commission),
            'montant_total':   str(reservation.montant),
            'statut_paiement': 'libere',
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  SIGNALER UN LITIGE
#  POST /api/reservations/<id>/litige/
# ──────────────────────────────────────────
class SignalerLitigeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        try:
            reservation = Reservation.objects.get(id_reservation=id_reservation)
        except Reservation.DoesNotExist:
            return Response({'error': 'Réservation introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        user            = request.user
        est_client      = hasattr(user, 'client')      and reservation.id_client == user.client
        est_prestataire = hasattr(user, 'prestataire') and reservation.id_prestataire == user.prestataire
        if not (est_client or est_prestataire):
            return Response({'error': 'Accès non autorisé.'}, status=status.HTTP_403_FORBIDDEN)

        if reservation.statut_paiement != 'bloque':
            return Response(
                {'error': 'Impossible de signaler un litige sur ce paiement.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservation.statut_paiement = 'litige'
        reservation.save()

        return Response({
            'message':         'Litige signalé. ServiceLink va examiner votre demande sous 48h.',
            'statut_paiement': 'litige',
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  ENVOYER UN MESSAGE TEXTE
# ──────────────────────────────────────────
class EnvoyerMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = EnvoyerMessageSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(id_expediteur=request.user)
            return Response({
                'message': 'Message envoyé !',
                'data': MessageSerializer(message, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  ENVOYER UNE PHOTO
# ──────────────────────────────────────────
class EnvoyerPhotoView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        serializer = EnvoyerPhotoSerializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save(id_expediteur=request.user)
            return Response({
                'message': 'Photo envoyée !',
                'data': MessageSerializer(message, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  MESSAGES D'UNE RÉSERVATION
# ──────────────────────────────────────────
class MessagesReservationView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class   = MessageSerializer

    def get_queryset(self):
        id_reservation = self.kwargs['id_reservation']
        return Message.objects.filter(id_reservation=id_reservation).order_by('date_envoi')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# ──────────────────────────────────────────
#  MARQUER MESSAGES COMME LUS
# ──────────────────────────────────────────
class MarquerMessagesLusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_reservation):
        Message.objects.filter(
            id_reservation=id_reservation,
            id_destinataire=request.user,
            est_lu=False
        ).update(est_lu=True)
        return Response({'message': 'Messages marqués comme lus.'})


# ──────────────────────────────────────────
#  MODIFIER UN MESSAGE
# ──────────────────────────────────────────
class ModifierMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, id_message):
        try:
            message = Message.objects.get(id_message=id_message, id_expediteur=request.user)
        except Message.DoesNotExist:
            return Response(
                {'error': 'Message introuvable ou non autorisé.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ModifierMessageSerializer(message, data=request.data, partial=True)
        if serializer.is_valid():
            message = serializer.save()
            return Response({
                'message': 'Message modifié !',
                'data': MessageSerializer(message, context={'request': request}).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  SUPPRIMER UN MESSAGE
# ──────────────────────────────────────────
class SupprimerMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_message):
        try:
            message = Message.objects.get(id_message=id_message, id_expediteur=request.user)
        except Message.DoesNotExist:
            return Response(
                {'error': 'Message introuvable ou non autorisé.'},
                status=status.HTTP_404_NOT_FOUND
            )

        message.delete()
        return Response({'message': 'Message supprimé.'}, status=status.HTTP_200_OK)