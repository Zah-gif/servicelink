from rest_framework import serializers
from .models import Paiement, Abonnement


# ──────────────────────────────────────────
#  Serializer PAIEMENT
# ──────────────────────────────────────────
class PaiementSerializer(serializers.ModelSerializer):

    reservation_statut = serializers.CharField(
        source='id_reservation.statut',
        read_only=True
    )

    class Meta:
        model  = Paiement
        fields = [
            'id_paiement',
            'id_reservation',
            'reservation_statut',
            'montant_paye',
            'operateur',
            'statut_paiement',
            'reference_paiement',
            'date_paiement',
            'date_reversement',
        ]
        read_only_fields = [
            'id_paiement', 'date_paiement',
            'date_reversement', 'reference_paiement'
        ]


# ──────────────────────────────────────────
#  Serializer CRÉER PAIEMENT
# ──────────────────────────────────────────
class CreerPaiementSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Paiement
        fields = ['id_reservation', 'montant_paye', 'operateur']


# ──────────────────────────────────────────
#  Serializer ABONNEMENT
# ──────────────────────────────────────────
class AbonnementSerializer(serializers.ModelSerializer):

    prestataire_nom    = serializers.CharField(
        source='id_prestataire.id_utilisateur.nom',
        read_only=True
    )
    prestataire_prenoms = serializers.CharField(
        source='id_prestataire.id_utilisateur.prenoms',
        read_only=True
    )

    class Meta:
        model  = Abonnement
        fields = [
            'id_abonnement',
            'id_prestataire',
            'prestataire_nom',
            'prestataire_prenoms',
            'type_offre',
            'montant_paye',
            'date_debut',
            'date_fin',
            'est_actif',
        ]
        read_only_fields = [
            'id_abonnement', 'date_debut',
            'date_fin', 'montant_paye'
        ]


# ──────────────────────────────────────────
#  Serializer SOUSCRIRE ABONNEMENT
# ──────────────────────────────────────────
class SouscrireAbonnementSerializer(serializers.Serializer):

    type_offre = serializers.ChoiceField(
        choices=['mensuel', 'annuel']
    )
    operateur  = serializers.ChoiceField(
        choices=['orange', 'mtn', 'wave', 'moov']
    )