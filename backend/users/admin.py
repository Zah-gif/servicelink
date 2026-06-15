from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Utilisateur, Client, Prestataire, Favori, MessageContact


# ──────────────────────────────────────────
#  UTILISATEUR
# ──────────────────────────────────────────
@admin.register(Utilisateur)
class UtilisateurAdmin(admin.ModelAdmin):
    list_display    = ('id_utilisateur', 'prenoms', 'nom', 'email', 'telephone', 'badge_actif', 'date_inscription')
    list_filter     = ('est_actif', 'is_staff', 'date_inscription')
    search_fields   = ('nom', 'prenoms', 'email', 'telephone')
    ordering        = ('-date_inscription',)
    readonly_fields = ('date_inscription', 'last_login')
    list_per_page   = 25

    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenoms', 'email', 'telephone')
        }),
        ('Statut du compte', {
            'fields': ('est_actif', 'is_staff', 'is_superuser')
        }),
        ('Dates', {
            'fields': ('date_inscription', 'last_login')
        }),
    )

    @admin.display(description='Statut')
    def badge_actif(self, obj):
        if obj.est_actif:
            return mark_safe('<span style="color:#065f46; font-weight:600;">● Actif</span>')
        return mark_safe('<span style="color:#991b1b; font-weight:600;">● Inactif</span>')


# ──────────────────────────────────────────
#  CLIENT
# ──────────────────────────────────────────
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('id_client', 'nom_complet', 'email', 'commune_residence')
    search_fields = ('id_utilisateur__nom', 'id_utilisateur__prenoms', 'id_utilisateur__email')
    list_filter   = ('commune_residence',)
    list_per_page = 25

    @admin.display(description='Client')
    def nom_complet(self, obj):
        return f"{obj.id_utilisateur.prenoms} {obj.id_utilisateur.nom}"

    @admin.display(description='Email')
    def email(self, obj):
        return obj.id_utilisateur.email


# ──────────────────────────────────────────
#  PRESTATAIRE
# ──────────────────────────────────────────
@admin.register(Prestataire)
class PrestataireAdmin(admin.ModelAdmin):
    list_display  = ('id_prestataire', 'nom_complet', 'email', 'note_moyenne',
                     'nombre_avis', 'badge_premium', 'badge_verifie', 'badge_disponible')
    list_filter   = ('est_premium', 'est_verifie', 'est_disponible', 'est_actif', 'badge_top')
    search_fields = ('id_utilisateur__nom', 'id_utilisateur__prenoms', 'id_utilisateur__email')
    ordering      = ('-note_moyenne',)
    list_per_page = 25

    fieldsets = (
        ('Prestataire', {
            'fields': ('id_utilisateur', 'description', 'photo_profil')
        }),
        ('Statut & Vérification', {
            'fields': ('est_verifie', 'est_premium', 'date_fin_premium', 'est_disponible', 'est_actif')
        }),
        ('Réputation', {
            'fields': ('note_moyenne', 'nombre_avis', 'badge_top')
        }),
    )

    @admin.display(description='Prestataire')
    def nom_complet(self, obj):
        return f"{obj.id_utilisateur.prenoms} {obj.id_utilisateur.nom}"

    @admin.display(description='Email')
    def email(self, obj):
        return obj.id_utilisateur.email

    @admin.display(description='Premium')
    def badge_premium(self, obj):
        if obj.est_premium:
            return mark_safe('<span style="color:#92400e; font-weight:600;">⭐ Premium</span>')
        return mark_safe('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Vérifié')
    def badge_verifie(self, obj):
        if obj.est_verifie:
            return mark_safe('<span style="color:#065f46; font-weight:600;">✓ Vérifié</span>')
        return mark_safe('<span style="color:#94a3b8;">—</span>')

    @admin.display(description='Disponible')
    def badge_disponible(self, obj):
        if obj.est_disponible:
            return mark_safe('<span style="color:#065f46;">● Oui</span>')
        return mark_safe('<span style="color:#991b1b;">● Non</span>')


# ──────────────────────────────────────────
#  FAVORI
# ──────────────────────────────────────────
@admin.register(Favori)
class FavoriAdmin(admin.ModelAdmin):
    list_display  = ('id_favori', 'client', 'prestataire', 'date_ajout')
    search_fields = ('id_client__id_utilisateur__nom', 'id_prestataire__id_utilisateur__nom')
    ordering      = ('-date_ajout',)
    list_per_page = 25

    @admin.display(description='Client')
    def client(self, obj):
        return f"{obj.id_client.id_utilisateur.prenoms} {obj.id_client.id_utilisateur.nom}"

    @admin.display(description='Prestataire')
    def prestataire(self, obj):
        return f"{obj.id_prestataire.id_utilisateur.prenoms} {obj.id_prestataire.id_utilisateur.nom}"


# ──────────────────────────────────────────
#  MESSAGE DE CONTACT
# ──────────────────────────────────────────
@admin.register(MessageContact)
class MessageContactAdmin(admin.ModelAdmin):
    list_display    = ('prenom', 'nom', 'email', 'sujet', 'date_envoi', 'badge_traite')
    list_filter     = ('est_traite', 'sujet', 'date_envoi')
    search_fields   = ('prenom', 'nom', 'email', 'sujet', 'message')
    ordering        = ('-date_envoi',)
    readonly_fields = ('prenom', 'nom', 'email', 'sujet', 'message', 'date_envoi')
    list_per_page   = 25

    fieldsets = (
        ('Expéditeur', {
            'fields': ('prenom', 'nom', 'email')
        }),
        ('Message', {
            'fields': ('sujet', 'message', 'date_envoi')
        }),
        ('Suivi', {
            'fields': ('est_traite',)
        }),
    )

    @admin.display(description='Statut')
    def badge_traite(self, obj):
        if obj.est_traite:
            return mark_safe('<span style="color:#065f46; font-weight:600;">✓ Traité</span>')
        return mark_safe('<span style="color:#92400e; font-weight:600;">● Non lu</span>')


# ──────────────────────────────────────────
#  Personnalisation de l'en-tête admin
# ──────────────────────────────────────────
admin.site.site_header = 'ServiceLink — Administration'
admin.site.site_title  = 'ServiceLink Admin'
admin.site.index_title = 'Gestion de la plateforme'