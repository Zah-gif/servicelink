from django.db import models
from users.models import Prestataire
from reservations.models import Reservation


# ──────────────────────────────────────────
#  Modèle PAIEMENT
# ──────────────────────────────────────────
class Paiement(models.Model):

    OPERATEUR_CHOICES = [
        ('orange', 'Orange Money'),
        ('mtn',    'MTN Mobile Money'),
        ('wave',   'Wave'),
        ('moov',   'Moov Money'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme',   'Confirmé'),
        ('reverse',    'Reversé'),
        ('bloque',     'Bloqué'),
    ]

    id_paiement        = models.AutoField(primary_key=True)
    id_reservation     = models.OneToOneField(
        Reservation,
        on_delete=models.RESTRICT,
        db_column='id_reservation',
        related_name='paiement'
    )
    montant_paye       = models.DecimalField(max_digits=10, decimal_places=2)
    operateur          = models.CharField(max_length=20, choices=OPERATEUR_CHOICES)
    statut_paiement    = models.CharField(max_length=50, choices=STATUT_CHOICES,
                                           default='en_attente')
    reference_paiement = models.CharField(max_length=100, unique=True,
                                           blank=True, null=True)
    date_paiement      = models.DateTimeField(auto_now_add=True)
    date_reversement   = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'paiement'
        verbose_name = 'Paiement'
        verbose_name_plural = 'Paiements'
        ordering = ['-date_paiement']

    def __str__(self):
        return f"Paiement #{self.id_paiement} — {self.montant_paye} FCFA — {self.statut_paiement}"


# ──────────────────────────────────────────
#  Modèle ABONNEMENT
# ──────────────────────────────────────────
class Abonnement(models.Model):

    TYPE_CHOICES = [
        ('mensuel', 'Mensuel — 5 000 FCFA'),
        ('annuel',  'Annuel — 50 000 FCFA'),
    ]

    id_abonnement  = models.AutoField(primary_key=True)
    id_prestataire = models.ForeignKey(
        Prestataire,
        on_delete=models.CASCADE,
        db_column='id_prestataire',
        related_name='abonnements'
    )
    type_offre     = models.CharField(max_length=20, choices=TYPE_CHOICES)
    montant_paye   = models.DecimalField(max_digits=10, decimal_places=2)
    date_debut     = models.DateField()
    date_fin       = models.DateField()
    est_actif      = models.BooleanField(default=True)

    class Meta:
        db_table = 'abonnement'
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
        ordering = ['-date_debut']

    def __str__(self):
        return f"Abonnement {self.type_offre} — {self.id_prestataire} — {self.est_actif}"