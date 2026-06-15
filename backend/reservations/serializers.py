from rest_framework import serializers
from .models import Reservation, Avis, Message


# ──────────────────────────────────────────
#  Serializer RESERVATION
# ──────────────────────────────────────────
class ReservationSerializer(serializers.ModelSerializer):

    client_nom                 = serializers.CharField(
        source='id_client.id_utilisateur.nom', read_only=True
    )
    client_prenoms             = serializers.CharField(
        source='id_client.id_utilisateur.prenoms', read_only=True
    )
    prestataire_nom            = serializers.CharField(
        source='id_prestataire.id_utilisateur.nom', read_only=True
    )
    prestataire_prenoms        = serializers.CharField(
        source='id_prestataire.id_utilisateur.prenoms', read_only=True
    )
    id_client_utilisateur      = serializers.IntegerField(
        source='id_client.id_utilisateur.id_utilisateur', read_only=True
    )
    id_prestataire_utilisateur = serializers.IntegerField(
        source='id_prestataire.id_utilisateur.id_utilisateur', read_only=True
    )
    service_titre              = serializers.CharField(
        source='id_service.titre', read_only=True
    )
    metier_nom                 = serializers.SerializerMethodField()
    categorie_nom              = serializers.SerializerMethodField()
    a_un_avis                  = serializers.SerializerMethodField()

    class Meta:
        model  = Reservation
        fields = [
            'id_reservation',
            'id_client_utilisateur',
            'id_prestataire_utilisateur',
            'client_nom', 'client_prenoms',
            'prestataire_nom', 'prestataire_prenoms',
            'service_titre', 'metier_nom', 'categorie_nom',
            'type_demande', 'statut',
            'description_besoin', 'date_souhaitee',
            'montant', 'date_creation', 'date_confirmation',
            'a_un_avis',
            # ── Paiement séquestre ──
            'statut_paiement',
            'code_validation',
            'montant_commission',
            'montant_prestataire',
            'mode_paiement',
            'telephone_paiement',
            'date_paiement',
            'date_liberation',
        ]
        read_only_fields = ['id_reservation', 'date_creation', 'date_confirmation']

    def get_metier_nom(self, obj):
        if obj.id_service:
            return obj.id_service.id_metier.nom_metier
        return None

    def get_categorie_nom(self, obj):
        if obj.id_service:
            return obj.id_service.id_categorie.nom_categorie
        return None

    def get_a_un_avis(self, obj):
        return hasattr(obj, 'avis')


# ──────────────────────────────────────────
#  Serializer CRÉATION RESERVATION
# ──────────────────────────────────────────
class CreerReservationSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Reservation
        fields = [
            'id_prestataire', 'id_service',
            'type_demande', 'description_besoin',
            'date_souhaitee', 'montant'
        ]

    def validate(self, data):
        service     = data.get('id_service')
        prestataire = data.get('id_prestataire')
        if service and prestataire:
            if service.id_prestataire != prestataire:
                raise serializers.ValidationError(
                    {'id_service': "Ce service n'appartient pas à ce prestataire."}
                )
        return data

    def create(self, validated_data):
        return Reservation.objects.create(**validated_data)


# ──────────────────────────────────────────
#  Serializer AVIS
# ──────────────────────────────────────────
class AvisSerializer(serializers.ModelSerializer):

    client_nom     = serializers.CharField(
        source='id_reservation.id_client.id_utilisateur.nom', read_only=True
    )
    client_prenoms = serializers.CharField(
        source='id_reservation.id_client.id_utilisateur.prenoms', read_only=True
    )

    class Meta:
        model  = Avis
        fields = [
            'id_avis', 'id_reservation',
            'client_nom', 'client_prenoms',
            'note', 'commentaire',
            'date_avis', 'est_modere',
        ]
        read_only_fields = ['id_avis', 'id_reservation', 'date_avis', 'est_modere']

    def validate_note(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("La note doit être entre 1 et 5.")
        return value


# ──────────────────────────────────────────
#  Serializer MESSAGE
# ──────────────────────────────────────────
class MessageSerializer(serializers.ModelSerializer):

    expediteur_nom     = serializers.CharField(
        source='id_expediteur.nom', read_only=True
    )
    expediteur_prenoms = serializers.CharField(
        source='id_expediteur.prenoms', read_only=True
    )
    photo_url          = serializers.SerializerMethodField()

    class Meta:
        model  = Message
        fields = [
            'id_message', 'id_reservation',
            'id_expediteur', 'id_destinataire',
            'expediteur_nom', 'expediteur_prenoms',
            'type_message', 'contenu', 'photo', 'photo_url',
            'date_envoi', 'est_lu',
        ]
        read_only_fields = ['id_message', 'date_envoi']

    def get_photo_url(self, obj):
        if obj.photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.photo.url)
            return obj.photo.url
        return None


# ──────────────────────────────────────────
#  Serializer ENVOI MESSAGE TEXTE
# ──────────────────────────────────────────
class EnvoyerMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Message
        fields = ['id_reservation', 'id_destinataire', 'contenu']

    def create(self, validated_data):
        validated_data['type_message'] = 'texte'
        return Message.objects.create(**validated_data)


# ──────────────────────────────────────────
#  Serializer ENVOI PHOTO
# ──────────────────────────────────────────
class EnvoyerPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Message
        fields = ['id_reservation', 'id_destinataire', 'photo']

    def validate_photo(self, value):
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("La photo ne doit pas dépasser 5 MB.")
        if not value.content_type.startswith('image/'):
            raise serializers.ValidationError("Le fichier doit être une image.")
        return value

    def create(self, validated_data):
        validated_data['type_message'] = 'photo'
        validated_data['contenu']      = '📷 Photo'
        return Message.objects.create(**validated_data)


# ──────────────────────────────────────────
#  Serializer MODIFIER MESSAGE
# ──────────────────────────────────────────
class ModifierMessageSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Message
        fields = ['contenu']