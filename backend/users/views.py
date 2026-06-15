from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.db import connection
from .models import Utilisateur, Client, Prestataire, Favori, MessageContact
from .serializers import (
    InscriptionClientSerializer,
    InscriptionPrestataireSerializer,
    UtilisateurSerializer,
    ClientSerializer,
    PrestataireSerializer,
    ChangerMotDePasseSerializer,
    MessageContactSerializer,
)
from services.models import Service
from services.serializers import ServiceSerializer, PrestataireRechercheSerializer
from reservations.models import Avis


# ──────────────────────────────────────────
#  INSCRIPTION CLIENT
# ──────────────────────────────────────────
class InscriptionClientView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionClientSerializer(data=request.data)
        if serializer.is_valid():
            utilisateur = serializer.save()
            refresh = RefreshToken.for_user(utilisateur)
            return Response({
                'message': 'Compte client créé avec succès !',
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
                'user':    UtilisateurSerializer(utilisateur).data,
                'type':    'client',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  INSCRIPTION PRESTATAIRE
# ──────────────────────────────────────────
class InscriptionPrestataireView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = InscriptionPrestataireSerializer(data=request.data)
        if serializer.is_valid():
            utilisateur = serializer.save()
            refresh = RefreshToken.for_user(utilisateur)
            return Response({
                'message': 'Compte prestataire créé avec succès !',
                'access':  str(refresh.access_token),
                'refresh': str(refresh),
                'user':    UtilisateurSerializer(utilisateur).data,
                'type':    'prestataire',
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  CONNEXION
# ──────────────────────────────────────────
class ConnexionView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email    = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email et mot de passe obligatoires.'}, status=status.HTTP_400_BAD_REQUEST)

        utilisateur = authenticate(request, username=email, password=password)

        if utilisateur is None:
            return Response({'error': 'Email ou mot de passe incorrect.'}, status=status.HTTP_401_UNAUTHORIZED)

        if not utilisateur.est_actif:
            return Response({'error': "Compte désactivé. Contactez l'administrateur."}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(utilisateur)

        type_utilisateur = 'inconnu'
        try:
            utilisateur.client
            type_utilisateur = 'client'
        except Client.DoesNotExist:
            pass
        try:
            utilisateur.prestataire
            type_utilisateur = 'prestataire'
        except Prestataire.DoesNotExist:
            pass

        return Response({
            'message': 'Connexion réussie !',
            'access':  str(refresh.access_token),
            'refresh': str(refresh),
            'user':    UtilisateurSerializer(utilisateur).data,
            'type':    type_utilisateur,
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  DÉCONNEXION
# ──────────────────────────────────────────
class DeconnexionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'message': 'Déconnexion réussie !'}, status=status.HTTP_200_OK)
        except Exception:
            return Response({'error': 'Token invalide.'}, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  PROFIL UTILISATEUR CONNECTÉ
# ──────────────────────────────────────────
class ProfilView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = UtilisateurSerializer(request.user).data
        # Si l'utilisateur est un prestataire, on ajoute sa photo de profil
        try:
            prestataire = request.user.prestataire
            photo_url = None
            if prestataire.photo_profil:
                photo_url = request.build_absolute_uri(prestataire.photo_profil.url)
            data['photo_profil'] = photo_url
            data['id_prestataire'] = prestataire.id_prestataire
        except Prestataire.DoesNotExist:
            pass
        return Response(data)

    def put(self, request):
        serializer = UtilisateurSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profil mis à jour !', 'user': serializer.data})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  UPLOAD PHOTO DE PROFIL PRESTATAIRE
# ──────────────────────────────────────────
class UploadPhotoProfilView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes     = [MultiPartParser, FormParser]

    def post(self, request):
        try:
            prestataire = request.user.prestataire
        except Prestataire.DoesNotExist:
            return Response({'error': 'Seuls les prestataires peuvent uploader une photo de profil.'}, status=status.HTTP_403_FORBIDDEN)

        photo = request.FILES.get('photo')
        if not photo:
            return Response({'error': 'Aucune photo fournie.'}, status=status.HTTP_400_BAD_REQUEST)

        if photo.size > 5 * 1024 * 1024:
            return Response({'error': 'La photo ne doit pas dépasser 5 MB.'}, status=status.HTTP_400_BAD_REQUEST)

        if not photo.content_type.startswith('image/'):
            return Response({'error': 'Le fichier doit être une image.'}, status=status.HTTP_400_BAD_REQUEST)

        if prestataire.photo_profil:
            try:
                prestataire.photo_profil.delete(save=False)
            except Exception:
                pass

        prestataire.photo_profil = photo
        prestataire.save()

        photo_url = request.build_absolute_uri(prestataire.photo_profil.url)
        return Response({'message': 'Photo de profil mise à jour !', 'photo_url': photo_url}, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  PROFIL PRESTATAIRE PUBLIC
# ──────────────────────────────────────────
class ProfilPrestatairePublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id_prestataire):
        try:
            prestataire = Prestataire.objects.get(id_prestataire=id_prestataire, est_actif=True)
        except Prestataire.DoesNotExist:
            return Response({'error': 'Prestataire introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        utilisateur = prestataire.id_utilisateur
        services    = Service.objects.filter(id_prestataire=prestataire, est_actif=True)

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT c.id_commune, c.nom_commune
                FROM commune c
                INNER JOIN intervient_dans i ON c.id_commune = i.id_commune
                WHERE i.id_prestataire = %s
            """, [prestataire.id_prestataire])
            communes = [{'id_commune': row[0], 'nom_commune': row[1]} for row in cursor.fetchall()]

        tous_avis = Avis.objects.filter(
            id_reservation__id_prestataire=prestataire, est_modere=False
        ).order_by('-date_avis')

        avis_data = [{
            'note':        a.note,
            'commentaire': a.commentaire,
            'date_avis':   a.date_avis.strftime('%d/%m/%Y'),
        } for a in tous_avis[:5]]

        total_avis       = tous_avis.count()
        repartition_avis = {}
        for note in [5, 4, 3, 2, 1]:
            count = tous_avis.filter(note=note).count()
            repartition_avis[note] = {
                'count':       count,
                'pourcentage': round((count / total_avis * 100)) if total_avis > 0 else 0,
            }

        from reservations.models import Reservation
        missions_terminees = Reservation.objects.filter(id_prestataire=prestataire, statut='terminee').count()
        membre_depuis      = utilisateur.date_inscription.strftime('%B %Y') if hasattr(utilisateur, 'date_inscription') else None

        photo_url = None
        if prestataire.photo_profil:
            photo_url = request.build_absolute_uri(prestataire.photo_profil.url)

        # Vérifier si le client connecté a mis ce prestataire en favori
        est_favori = False
        if request.user.is_authenticated:
            try:
                client = request.user.client
                est_favori = Favori.objects.filter(
                    id_client=client,
                    id_prestataire=prestataire
                ).exists()
            except Client.DoesNotExist:
                pass

        return Response({
            'id_prestataire':     prestataire.id_prestataire,
            'nom':                utilisateur.nom,
            'prenoms':            utilisateur.prenoms,
            'description':        prestataire.description,
            'photo_profil':       photo_url,
            'est_premium':        prestataire.est_premium,
            'est_verifie':        prestataire.est_verifie,
            'est_disponible':     prestataire.est_disponible,
            'note_moyenne':       str(prestataire.note_moyenne),
            'nombre_avis':        prestataire.nombre_avis,
            'badge_top':          prestataire.badge_top,
            'communes':           communes,
            'services':           ServiceSerializer(services, many=True).data,
            'avis':               avis_data,
            'repartition_avis':   repartition_avis,
            'missions_terminees': missions_terminees,
            'membre_depuis':      membre_depuis,
            'est_favori':         est_favori,
        }, status=status.HTTP_200_OK)


# ──────────────────────────────────────────
#  TOGGLE FAVORI
#  POST /api/users/favoris/<id_prestataire>/
#  — Ajoute si pas encore favori, retire sinon
# ──────────────────────────────────────────
class ToggleFavoriView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id_prestataire):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response(
                {'error': 'Seuls les clients peuvent gérer les favoris.'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            prestataire = Prestataire.objects.get(id_prestataire=id_prestataire, est_actif=True)
        except Prestataire.DoesNotExist:
            return Response({'error': 'Prestataire introuvable.'}, status=status.HTTP_404_NOT_FOUND)

        favori, created = Favori.objects.get_or_create(
            id_client=client,
            id_prestataire=prestataire
        )

        if not created:
            # Déjà en favori → on retire
            favori.delete()
            return Response({
                'message': 'Retiré des favoris.',
                'est_favori': False,
            }, status=status.HTTP_200_OK)

        return Response({
            'message': 'Ajouté aux favoris !',
            'est_favori': True,
        }, status=status.HTTP_201_CREATED)


# ──────────────────────────────────────────
#  MES FAVORIS
#  GET /api/users/favoris/
# ──────────────────────────────────────────
class MesFavorisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            client = request.user.client
        except Client.DoesNotExist:
            return Response(
                {'error': 'Seuls les clients peuvent voir leurs favoris.'},
                status=status.HTTP_403_FORBIDDEN
            )

        favoris = Favori.objects.filter(id_client=client).select_related(
            'id_prestataire__id_utilisateur'
        ).order_by('-date_ajout')

        data = []
        for f in favoris:
            prestataire = f.id_prestataire
            utilisateur = prestataire.id_utilisateur

            # Service principal
            service = prestataire.services.filter(est_actif=True).first()
            metier_nom    = service.id_metier.nom_metier if service else None
            categorie_nom = service.id_categorie.nom_categorie if service else None
            tarif_affiche = service.tarif_affiche if service else None

            # Photo
            photo_url = None
            if prestataire.photo_profil:
                photo_url = request.build_absolute_uri(prestataire.photo_profil.url)

            data.append({
                'id_prestataire': prestataire.id_prestataire,
                'nom':            utilisateur.nom,
                'prenoms':        utilisateur.prenoms,
                'photo_profil':   photo_url,
                'metier_nom':     metier_nom,
                'categorie_nom':  categorie_nom,
                'tarif_affiche':  tarif_affiche,
                'note_moyenne':   str(prestataire.note_moyenne),
                'nombre_avis':    prestataire.nombre_avis,
                'est_disponible': prestataire.est_disponible,
                'est_premium':    prestataire.est_premium,
                'est_verifie':    prestataire.est_verifie,
                'date_ajout':     f.date_ajout.strftime('%d/%m/%Y'),
            })

        return Response({'count': len(data), 'results': data})


# ──────────────────────────────────────────
#  CHANGER MOT DE PASSE
# ──────────────────────────────────────────
class ChangerMotDePasseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangerMotDePasseSerializer(data=request.data)
        if serializer.is_valid():
            utilisateur = request.user
            if not utilisateur.check_password(serializer.validated_data['ancien_mot_de_passe']):
                return Response({'error': 'Ancien mot de passe incorrect.'}, status=status.HTTP_400_BAD_REQUEST)
            utilisateur.set_password(serializer.validated_data['nouveau_mot_de_passe'])
            utilisateur.save()
            return Response({'message': 'Mot de passe changé avec succès !'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ──────────────────────────────────────────
#  ENVOYER UN MESSAGE DE CONTACT
#  POST /api/users/contact/  (public)
# ──────────────────────────────────────────
class ContactView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MessageContactSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Votre message a bien été envoyé ! Nous vous répondrons sous 24h.'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)