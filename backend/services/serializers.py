from rest_framework import serializers
from .models import Categorie, Metier, Commune, Service
from users.models import Prestataire


# ──────────────────────────────────────────
#  Serializer CATEGORIE
# ──────────────────────────────────────────
class CategorieSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Categorie
        fields = ['id_categorie', 'nom_categorie', 'icone', 'est_active']


# ──────────────────────────────────────────
#  Serializer METIER
# ──────────────────────────────────────────
class MetierSerializer(serializers.ModelSerializer):

    categorie_nom = serializers.CharField(
        source='id_categorie.nom_categorie',
        read_only=True
    )

    class Meta:
        model  = Metier
        fields = ['id_metier', 'nom_metier', 'categorie_nom', 'est_actif']


# ──────────────────────────────────────────
#  Serializer COMMUNE
# ──────────────────────────────────────────
class CommuneSerializer(serializers.ModelSerializer):

    class Meta:
        model  = Commune
        fields = ['id_commune', 'nom_commune', 'latitude', 'longitude']


# ──────────────────────────────────────────
#  Serializer SERVICE
# ──────────────────────────────────────────
class ServiceSerializer(serializers.ModelSerializer):

    prestataire_nom     = serializers.CharField(
        source='id_prestataire.id_utilisateur.nom',
        read_only=True
    )
    prestataire_prenoms = serializers.CharField(
        source='id_prestataire.id_utilisateur.prenoms',
        read_only=True
    )
    metier_nom          = serializers.CharField(
        source='id_metier.nom_metier',
        read_only=True
    )
    categorie_nom       = serializers.CharField(
        source='id_categorie.nom_categorie',
        read_only=True
    )
    # Plages formatées en lecture seule
    tarif_affiche       = serializers.SerializerMethodField()
    duree_affichee      = serializers.SerializerMethodField()

    class Meta:
        model  = Service
        fields = [
            'id_service',
            'id_prestataire',
            'prestataire_nom',
            'prestataire_prenoms',
            'id_metier',
            'metier_nom',
            'id_categorie',
            'categorie_nom',
            'titre',
            'description',
            # Plages de prix
            'tarif_min',
            'tarif_max',
            'tarif_affiche',
            # Plages de durée
            'duree_min',
            'duree_max',
            'duree_affichee',
            'est_actif',
            'date_creation',
        ]
        read_only_fields = ['id_service', 'date_creation']

    def get_tarif_affiche(self, obj):
        if obj.tarif_min and obj.tarif_max:
            return f"{int(obj.tarif_min):,} — {int(obj.tarif_max):,} FCFA".replace(',', ' ')
        elif obj.tarif_min:
            return f"À partir de {int(obj.tarif_min):,} FCFA".replace(',', ' ')
        elif obj.tarif_max:
            return f"Jusqu'à {int(obj.tarif_max):,} FCFA".replace(',', ' ')
        return "Prix sur devis"

    def get_duree_affichee(self, obj):
        if obj.duree_min and obj.duree_max:
            return f"{obj.duree_min} — {obj.duree_max} min"
        elif obj.duree_min:
            return f"À partir de {obj.duree_min} min"
        elif obj.duree_max:
            return f"Jusqu'à {obj.duree_max} min"
        return None


# ──────────────────────────────────────────
#  Serializer PRESTATAIRE RECHERCHE
# ──────────────────────────────────────────
class PrestataireRechercheSerializer(serializers.ModelSerializer):

    nom           = serializers.CharField(
        source='id_utilisateur.nom', read_only=True
    )
    prenoms       = serializers.CharField(
        source='id_utilisateur.prenoms', read_only=True
    )
    metier_nom    = serializers.SerializerMethodField()
    categorie_nom = serializers.SerializerMethodField()
    tarif_min     = serializers.SerializerMethodField()

    class Meta:
        model  = Prestataire
        fields = [
            'id_prestataire',
            'nom', 'prenoms',
            'photo_profil',
            'metier_nom',
            'categorie_nom',
            'tarif_min',
            'note_moyenne',
            'nombre_avis',
            'est_premium',
            'est_verifie',
            'badge_top',
            'est_disponible',
        ]

    def get_metier_nom(self, obj):
        service = obj.services.filter(est_actif=True).first()
        return service.id_metier.nom_metier if service else None

    def get_categorie_nom(self, obj):
        service = obj.services.filter(est_actif=True).first()
        return service.id_categorie.nom_categorie if service else None

    def get_tarif_min(self, obj):
        """Retourne le tarif minimum parmi tous les services actifs"""
        services = obj.services.filter(est_actif=True, tarif_min__isnull=False)
        if services.exists():
            min_tarif = min(s.tarif_min for s in services)
            return f"À partir de {int(min_tarif):,} FCFA".replace(',', ' ')
        return None