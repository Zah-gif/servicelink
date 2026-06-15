from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Categorie, Metier, Commune, Service


# ──────────────────────────────────────────
#  CATEGORIE
# ──────────────────────────────────────────
@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display  = ('id_categorie', 'nom_categorie', 'nombre_metiers', 'badge_active')
    list_filter   = ('est_active',)
    search_fields = ('nom_categorie',)
    ordering      = ('nom_categorie',)
    list_per_page = 25

    @admin.display(description='Nombre de métiers')
    def nombre_metiers(self, obj):
        return obj.metiers.count()

    @admin.display(description='Statut')
    def badge_active(self, obj):
        if obj.est_active:
            return mark_safe('<span style="color:#065f46; font-weight:600;">● Active</span>')
        return mark_safe('<span style="color:#991b1b; font-weight:600;">● Inactive</span>')


# ──────────────────────────────────────────
#  METIER
# ──────────────────────────────────────────
@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display  = ('id_metier', 'nom_metier', 'categorie', 'badge_actif')
    list_filter   = ('est_actif', 'id_categorie')
    search_fields = ('nom_metier',)
    ordering      = ('nom_metier',)
    list_per_page = 25

    @admin.display(description='Catégorie')
    def categorie(self, obj):
        return obj.id_categorie.nom_categorie

    @admin.display(description='Statut')
    def badge_actif(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:#065f46; font-weight:600;">● Actif</span>')
        return mark_safe('<span style="color:#991b1b; font-weight:600;">● Inactif</span>')


# ──────────────────────────────────────────
#  COMMUNE
# ──────────────────────────────────────────
@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display  = ('id_commune', 'nom_commune', 'latitude', 'longitude')
    search_fields = ('nom_commune',)
    ordering      = ('nom_commune',)
    list_per_page = 25


# ──────────────────────────────────────────
#  SERVICE
# ──────────────────────────────────────────
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display  = ('id_service', 'titre', 'prestataire', 'metier',
                     'categorie', 'tarif_affiche', 'badge_actif', 'date_creation')
    list_filter   = ('est_actif', 'id_categorie', 'id_metier', 'date_creation')
    search_fields = ('titre', 'description', 'id_prestataire__id_utilisateur__nom')
    ordering      = ('-date_creation',)
    readonly_fields = ('date_creation',)
    list_per_page = 25

    fieldsets = (
        ('Service', {
            'fields': ('id_prestataire', 'titre', 'description')
        }),
        ('Classification', {
            'fields': ('id_categorie', 'id_metier')
        }),
        ('Tarification', {
            'fields': ('tarif_min', 'tarif_max', 'duree_min', 'duree_max')
        }),
        ('Statut', {
            'fields': ('est_actif', 'date_creation')
        }),
    )

    @admin.display(description='Prestataire')
    def prestataire(self, obj):
        return f"{obj.id_prestataire.id_utilisateur.prenoms} {obj.id_prestataire.id_utilisateur.nom}"

    @admin.display(description='Métier')
    def metier(self, obj):
        return obj.id_metier.nom_metier

    @admin.display(description='Catégorie')
    def categorie(self, obj):
        return obj.id_categorie.nom_categorie

    @admin.display(description='Statut')
    def badge_actif(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:#065f46; font-weight:600;">● Actif</span>')
        return mark_safe('<span style="color:#991b1b; font-weight:600;">● Inactif</span>')