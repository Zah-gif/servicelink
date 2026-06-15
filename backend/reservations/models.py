from django.db import models
from django.utils.crypto import get_random_string
from users.models import Utilisateur, Client, Prestataire
from services.models import Service


# ──────────────────────────────────────────
#  Modèle RESERVATION
# ──────────────────────────────────────────
class Reservation(models.Model):

    STATUT_CHOICES = [
        ('en_attente',      'En attente'),
        ('paiement_requis', 'Paiement requis'),  # ← NOUVEAU
        ('confirmee',       'Confirmée'),
        ('en_cours',        'En cours'),
        ('terminee',        'Terminée'),
        ('annulee',         'Annulée'),
    ]

    TYPE_CHOICES = [
        ('directe', 'Réservation directe'),
        ('devis',   'Demande de devis'),
    ]

    STATUT_PAIEMENT_CHOICES = [
        ('non_paye',  'Non payé'),
        ('bloque',    'Payé — En attente de validation'),
        ('libere',    'Libéré au prestataire'),
        ('rembourse', 'Remboursé au client'),
        ('litige',    'En litige'),
    ]

    id_reservation      = models.AutoField(primary_key=True)
    id_client           = models.ForeignKey(
        Client, on_delete=models.RESTRICT,
        db_column='id_client', related_name='reservations'
    )
    id_prestataire      = models.ForeignKey(
        Prestataire, on_delete=models.RESTRICT,
        db_column='id_prestataire', related_name='reservations'
    )
    id_service          = models.ForeignKey(
        Service, on_delete=models.RESTRICT,
        db_column='id_service', related_name='reservations',
        blank=True, null=True
    )
    type_demande        = models.CharField(max_length=20, choices=TYPE_CHOICES)
    statut              = models.CharField(
        max_length=20, choices=STATUT_CHOICES, default='en_attente'
    )
    description_besoin  = models.TextField(blank=True, null=True)
    date_souhaitee      = models.DateField(blank=True, null=True)
    montant             = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True
    )
    date_creation       = models.DateTimeField(auto_now_add=True)
    date_confirmation   = models.DateTimeField(blank=True, null=True)

    # ── Paiement séquestre ──
    statut_paiement     = models.CharField(
        max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='non_paye'
    )
    code_validation     = models.CharField(
        max_length=8, blank=True, null=True,
        help_text='Code donné au client après paiement'
    )
    taux_commission     = models.DecimalField(
        max_digits=5, decimal_places=2, default=5.00,
        help_text='Commission ServiceLink en %'
    )
    montant_commission  = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text='Montant de la commission ServiceLink'
    )
    montant_prestataire = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        help_text='Montant net reçu par le prestataire'
    )
    mode_paiement       = models.CharField(
        max_length=20, blank=True, null=True,
        help_text='orange / mtn / wave'
    )
    telephone_paiement  = models.CharField(
        max_length=20, blank=True, null=True,
        help_text='Numéro utilisé pour le paiement'
    )
    date_paiement       = models.DateTimeField(blank=True, null=True)
    date_liberation     = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table     = 'reservation'
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-date_creation']

    def __str__(self):
        return f"Réservation #{self.id_reservation} — {self.statut}"

    def generer_code_validation(self):
        """Génère un code unique de 6 caractères ex: SL4892"""
        code = 'SL' + get_random_string(4, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        self.code_validation = code
        return code

    def calculer_commission(self):
        """Calcule la commission et le montant net prestataire"""
        if self.montant:
            self.montant_commission  = round(self.montant * self.taux_commission / 100, 2)
            self.montant_prestataire = round(self.montant - self.montant_commission, 2)


# ──────────────────────────────────────────
#  Modèle AVIS
# ──────────────────────────────────────────
class Avis(models.Model):

    id_avis        = models.AutoField(primary_key=True)
    id_reservation = models.OneToOneField(
        Reservation, on_delete=models.CASCADE,
        db_column='id_reservation', related_name='avis'
    )
    note           = models.IntegerField()
    commentaire    = models.TextField(blank=True, null=True)
    date_avis      = models.DateTimeField(auto_now_add=True)
    est_modere     = models.BooleanField(default=False)

    class Meta:
        db_table     = 'avis'
        verbose_name = 'Avis'
        verbose_name_plural = 'Avis'
        ordering = ['-date_avis']

    def __str__(self):
        return f"Avis #{self.id_avis} — Note : {self.note}/5"

    def save(self, *args, **kwargs):
        if not 1 <= self.note <= 5:
            raise ValueError("La note doit être entre 1 et 5")
        super().save(*args, **kwargs)


# ──────────────────────────────────────────
#  Modèle MESSAGE
# ──────────────────────────────────────────
class Message(models.Model):

    TYPE_CHOICES = [
        ('texte', 'Texte'),
        ('photo', 'Photo'),
    ]

    id_message      = models.AutoField(primary_key=True)
    id_reservation  = models.ForeignKey(
        Reservation, on_delete=models.CASCADE,
        db_column='id_reservation', related_name='messages'
    )
    id_expediteur   = models.ForeignKey(
        Utilisateur, on_delete=models.RESTRICT,
        db_column='id_expediteur', related_name='messages_envoyes'
    )
    id_destinataire = models.ForeignKey(
        Utilisateur, on_delete=models.RESTRICT,
        db_column='id_destinataire', related_name='messages_recus'
    )
    type_message    = models.CharField(max_length=10, choices=TYPE_CHOICES, default='texte')
    contenu         = models.TextField(blank=True, null=True)
    photo           = models.ImageField(
        upload_to='messages/photos/%Y/%m/', blank=True, null=True
    )
    date_envoi      = models.DateTimeField(auto_now_add=True)
    est_lu          = models.BooleanField(default=False)

    class Meta:
        db_table     = 'message'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['date_envoi']

    def __str__(self):
        return f"Message #{self.id_message} — {self.id_expediteur} → {self.id_destinataire}"