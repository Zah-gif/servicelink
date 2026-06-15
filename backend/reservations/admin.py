from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Reservation, Avis, Message


# ──────────────────────────────────────────
#  RESERVATION
# ──────────────────────────────────────────
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display  = ('id_reservation', 'client', 'prestataire', 'service_titre',
                     'badge_statut', 'badge_paiement', 'montant_format', 'date_creation')
    list_filter   = ('statut', 'statut_paiement', 'type_demande', 'mode_paiement', 'date_creation')
    search_fields = ('id_client__id_utilisateur__nom', 'id_prestataire__id_utilisateur__nom',
                     'code_validation')
    ordering      = ('-date_creation',)
    readonly_fields = ('date_creation', 'date_confirmation', 'date_paiement',
                       'date_liberation', 'code_validation',
                       'montant_commission', 'montant_prestataire')
    list_per_page = 25

    fieldsets = (
        ('Réservation', {
            'fields': ('id_client', 'id_prestataire', 'id_service', 'type_demande',
                       'statut', 'description_besoin', 'date_souhaitee')
        }),
        ('Montant & Paiement', {
            'fields': ('montant', 'statut_paiement', 'mode_paiement', 'telephone_paiement',
                       'taux_commission', 'montant_commission', 'montant_prestataire',
                       'code_validation')
        }),
        ('Dates', {
            'fields': ('date_creation', 'date_confirmation', 'date_paiement', 'date_liberation')
        }),
    )

    @admin.display(description='Client')
    def client(self, obj):
        return f"{obj.id_client.id_utilisateur.prenoms} {obj.id_client.id_utilisateur.nom}"

    @admin.display(description='Prestataire')
    def prestataire(self, obj):
        return f"{obj.id_prestataire.id_utilisateur.prenoms} {obj.id_prestataire.id_utilisateur.nom}"

    @admin.display(description='Service')
    def service_titre(self, obj):
        return obj.id_service.titre if obj.id_service else '—'

    @admin.display(description='Montant')
    def montant_format(self, obj):
        if obj.montant:
            return f"{int(obj.montant):,} FCFA"
        return '—'

    @admin.display(description='Statut')
    def badge_statut(self, obj):
        couleurs = {
            'en_attente':      ('#92400e', 'En attente'),
            'paiement_requis': ('#1e40af', 'Paiement requis'),
            'confirmee':       ('#065f46', 'Confirmée'),
            'en_cours':        ('#5b21b6', 'En cours'),
            'terminee':        ('#374151', 'Terminée'),
            'annulee':         ('#991b1b', 'Annulée'),
        }
        couleur, label = couleurs.get(obj.statut, ('#94a3b8', obj.statut))
        return format_html('<span style="color:{}; font-weight:600;">● {}</span>', couleur, label)

    @admin.display(description='Paiement')
    def badge_paiement(self, obj):
        couleurs = {
            'non_paye':  ('#94a3b8', 'Non payé'),
            'bloque':    ('#92400e', '🔒 Bloqué'),
            'libere':    ('#065f46', '✓ Libéré'),
            'rembourse': ('#991b1b', '↩ Remboursé'),
            'litige':    ('#991b1b', '⚠ Litige'),
        }
        couleur, label = couleurs.get(obj.statut_paiement, ('#94a3b8', obj.statut_paiement))
        return format_html('<span style="color:{}; font-weight:600;">{}</span>', couleur, label)


# ──────────────────────────────────────────
#  AVIS
# ──────────────────────────────────────────
@admin.register(Avis)
class AvisAdmin(admin.ModelAdmin):
    list_display  = ('id_avis', 'prestataire', 'client', 'etoiles',
                     'apercu_commentaire', 'badge_modere', 'date_avis')
    list_filter   = ('note', 'est_modere', 'date_avis')
    search_fields = ('commentaire', 'id_reservation__id_prestataire__id_utilisateur__nom')
    ordering      = ('-date_avis',)
    readonly_fields = ('date_avis',)
    list_per_page = 25

    @admin.display(description='Prestataire')
    def prestataire(self, obj):
        u = obj.id_reservation.id_prestataire.id_utilisateur
        return f"{u.prenoms} {u.nom}"

    @admin.display(description='Client')
    def client(self, obj):
        u = obj.id_reservation.id_client.id_utilisateur
        return f"{u.prenoms} {u.nom}"

    @admin.display(description='Note')
    def etoiles(self, obj):
        pleines = '★' * obj.note
        vides   = '☆' * (5 - obj.note)
        return format_html('<span style="color:#f59e0b; font-size:15px;">{}{}</span>', pleines, vides)

    @admin.display(description='Commentaire')
    def apercu_commentaire(self, obj):
        if obj.commentaire:
            return obj.commentaire[:50] + ('...' if len(obj.commentaire) > 50 else '')
        return '—'

    @admin.display(description='Modéré')
    def badge_modere(self, obj):
        if obj.est_modere:
            return mark_safe('<span style="color:#065f46;">✓ Oui</span>')
        return mark_safe('<span style="color:#94a3b8;">—</span>')


# ──────────────────────────────────────────
#  MESSAGE
# ──────────────────────────────────────────
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ('id_message', 'expediteur', 'destinataire', 'type_message',
                     'apercu_contenu', 'badge_lu', 'date_envoi')
    list_filter   = ('type_message', 'est_lu', 'date_envoi')
    search_fields = ('contenu', 'id_expediteur__nom', 'id_destinataire__nom')
    ordering      = ('-date_envoi',)
    readonly_fields = ('date_envoi',)
    list_per_page = 25

    @admin.display(description='Expéditeur')
    def expediteur(self, obj):
        return f"{obj.id_expediteur.prenoms} {obj.id_expediteur.nom}"

    @admin.display(description='Destinataire')
    def destinataire(self, obj):
        return f"{obj.id_destinataire.prenoms} {obj.id_destinataire.nom}"

    @admin.display(description='Contenu')
    def apercu_contenu(self, obj):
        if obj.contenu:
            return obj.contenu[:40] + ('...' if len(obj.contenu) > 40 else '')
        return '📷 Photo' if obj.type_message == 'photo' else '—'

    @admin.display(description='Lu')
    def badge_lu(self, obj):
        if obj.est_lu:
            return mark_safe('<span style="color:#065f46;">✓ Lu</span>')
        return mark_safe('<span style="color:#92400e;">● Non lu</span>')