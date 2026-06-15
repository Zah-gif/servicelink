from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Utilisateur, Client, Prestataire, MessageContact
from services.models import Metier, Categorie, Commune, Service


# ──────────────────────────────────────────
#  Serializer INSCRIPTION CLIENT
# ──────────────────────────────────────────
class InscriptionClientSerializer(serializers.ModelSerializer):

    password         = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model  = Utilisateur
        fields = [
            'nom', 'prenoms', 'email', 'telephone',
            'password', 'password_confirm'
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )
        validate_password(data['password'])
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        utilisateur = Utilisateur.objects.create_user(
            password=password, **validated_data
        )
        Client.objects.create(id_utilisateur=utilisateur)
        return utilisateur


# ──────────────────────────────────────────
#  Serializer INSCRIPTION PRESTATAIRE
# ──────────────────────────────────────────
class InscriptionPrestataireSerializer(serializers.ModelSerializer):

    password         = serializers.CharField(write_only=True, required=True)
    password_confirm = serializers.CharField(write_only=True, required=True)
    communes         = serializers.PrimaryKeyRelatedField(
        queryset=Commune.objects.all(),
        many=True, write_only=True, required=False
    )

    # ── Champs du premier service ──
    id_metier             = serializers.PrimaryKeyRelatedField(
        queryset=Metier.objects.all(), write_only=True
    )
    id_categorie          = serializers.PrimaryKeyRelatedField(
        queryset=Categorie.objects.all(), write_only=True
    )
    service_titre         = serializers.CharField(write_only=True, required=True)
    service_description   = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    # Plages de prix
    service_tarif_min     = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        write_only=True, required=False, allow_null=True
    )
    service_tarif_max     = serializers.DecimalField(
        max_digits=10, decimal_places=2,
        write_only=True, required=False, allow_null=True
    )
    # Plages de durée
    service_duree_min     = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )
    service_duree_max     = serializers.IntegerField(
        write_only=True, required=False, allow_null=True
    )

    class Meta:
        model  = Utilisateur
        fields = [
            'nom', 'prenoms', 'email', 'telephone',
            'password', 'password_confirm',
            'communes',
            'id_metier', 'id_categorie',
            'service_titre', 'service_description',
            'service_tarif_min', 'service_tarif_max',
            'service_duree_min', 'service_duree_max',
        ]

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError(
                {"password": "Les mots de passe ne correspondent pas."}
            )
        validate_password(data['password'])
        # Vérifier que tarif_min <= tarif_max
        tarif_min = data.get('service_tarif_min')
        tarif_max = data.get('service_tarif_max')
        if tarif_min and tarif_max and tarif_min > tarif_max:
            raise serializers.ValidationError(
                {"service_tarif_min": "Le prix minimum doit être inférieur au prix maximum."}
            )
        # Vérifier que duree_min <= duree_max
        duree_min = data.get('service_duree_min')
        duree_max = data.get('service_duree_max')
        if duree_min and duree_max and duree_min > duree_max:
            raise serializers.ValidationError(
                {"service_duree_min": "La durée minimum doit être inférieure à la durée maximum."}
            )
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password              = validated_data.pop('password')
        id_metier             = validated_data.pop('id_metier')
        id_categorie          = validated_data.pop('id_categorie')
        communes              = validated_data.pop('communes', [])
        service_titre         = validated_data.pop('service_titre')
        service_description   = validated_data.pop('service_description', '')
        service_tarif_min     = validated_data.pop('service_tarif_min', None)
        service_tarif_max     = validated_data.pop('service_tarif_max', None)
        service_duree_min     = validated_data.pop('service_duree_min', None)
        service_duree_max     = validated_data.pop('service_duree_max', None)

        # 1. Créer l'utilisateur
        utilisateur = Utilisateur.objects.create_user(
            password=password, **validated_data
        )

        # 2. Créer le profil prestataire
        prestataire = Prestataire.objects.create(
            id_utilisateur=utilisateur,
        )

        # 3. Associer les communes
        if communes:
            from django.db import connection
            with connection.cursor() as cursor:
                for commune in communes:
                    cursor.execute(
                        "INSERT INTO intervient_dans (id_prestataire, id_commune) VALUES (%s, %s)",
                        [prestataire.id_prestataire, commune.id_commune]
                    )

        # 4. Créer le premier service avec plages
        Service.objects.create(
            id_prestataire  = prestataire,
            id_metier       = id_metier,
            id_categorie    = id_categorie,
            titre           = service_titre,
            description     = service_description,
            tarif_min       = service_tarif_min,
            tarif_max       = service_tarif_max,
            duree_min       = service_duree_min,
            duree_max       = service_duree_max,
            est_actif       = True,
        )

        return utilisateur


# ──────────────────────────────────────────
#  Serializer PROFIL UTILISATEUR
# ──────────────────────────────────────────
class UtilisateurSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Utilisateur
        fields = [
            'id_utilisateur', 'nom', 'prenoms',
            'email', 'telephone', 'est_actif', 'date_inscription'
        ]
        read_only_fields = ['id_utilisateur', 'date_inscription']


# ──────────────────────────────────────────
#  Serializer PROFIL CLIENT
# ──────────────────────────────────────────
class ClientSerializer(serializers.ModelSerializer):

    utilisateur = UtilisateurSerializer(source='id_utilisateur', read_only=True)

    class Meta:
        model  = Client
        fields = ['id_client', 'utilisateur', 'commune_residence']


# ──────────────────────────────────────────
#  Serializer PROFIL PRESTATAIRE
# ──────────────────────────────────────────
class PrestataireSerializer(serializers.ModelSerializer):

    utilisateur = UtilisateurSerializer(source='id_utilisateur', read_only=True)

    class Meta:
        model  = Prestataire
        fields = [
            'id_prestataire', 'utilisateur',
            'description', 'photo_profil',
            'est_premium', 'est_verifie',
            'note_moyenne', 'badge_top', 'nombre_avis',
            'est_actif', 'est_disponible',
        ]


# ──────────────────────────────────────────
#  Serializer CHANGEMENT MOT DE PASSE
# ──────────────────────────────────────────
class ChangerMotDePasseSerializer(serializers.Serializer):

    ancien_mot_de_passe  = serializers.CharField(required=True)
    nouveau_mot_de_passe = serializers.CharField(required=True)
    confirmation         = serializers.CharField(required=True)

    def validate(self, data):
        if data['nouveau_mot_de_passe'] != data['confirmation']:
            raise serializers.ValidationError(
                {"confirmation": "Les mots de passe ne correspondent pas."}
            )
        validate_password(data['nouveau_mot_de_passe'])
        return data


# ──────────────────────────────────────────
#  Serializer MESSAGE DE CONTACT
# ──────────────────────────────────────────
class MessageContactSerializer(serializers.ModelSerializer):

    class Meta:
        model  = MessageContact
        fields = ['prenom', 'nom', 'email', 'sujet', 'message']