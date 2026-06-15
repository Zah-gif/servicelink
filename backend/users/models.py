from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


# ──────────────────────────────────────────
#  Manager personnalisé pour Utilisateur
# ──────────────────────────────────────────
class UtilisateurManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('est_actif', True)
        return self.create_user(email, password, **extra_fields)


# ──────────────────────────────────────────
#  Modèle UTILISATEUR
# ──────────────────────────────────────────
class Utilisateur(AbstractBaseUser, PermissionsMixin):

    id_utilisateur   = models.AutoField(primary_key=True)
    nom              = models.CharField(max_length=50)
    prenoms          = models.CharField(max_length=50)
    email            = models.EmailField(max_length=50, unique=True)
    telephone        = models.CharField(max_length=50, unique=True)
    est_actif        = models.BooleanField(default=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    is_staff         = models.BooleanField(default=False)
    password         = models.CharField(max_length=255, db_column='mot_de_passe')

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nom', 'prenoms', 'telephone']

    objects = UtilisateurManager()

    class Meta:
        db_table     = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f"{self.prenoms} {self.nom} ({self.email})"


# ──────────────────────────────────────────
#  Modèle CLIENT
# ──────────────────────────────────────────
class Client(models.Model):

    id_client         = models.AutoField(primary_key=True)
    id_utilisateur    = models.OneToOneField(
        Utilisateur, on_delete=models.CASCADE,
        db_column='id_utilisateur', related_name='client'
    )
    commune_residence = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table     = 'client'
        verbose_name = 'Client'
        verbose_name_plural = 'Clients'

    def __str__(self):
        return f"Client : {self.id_utilisateur.prenoms} {self.id_utilisateur.nom}"


# ──────────────────────────────────────────
#  Modèle PRESTATAIRE
# ──────────────────────────────────────────
class Prestataire(models.Model):

    id_prestataire   = models.AutoField(primary_key=True)
    id_utilisateur   = models.OneToOneField(
        Utilisateur, on_delete=models.CASCADE,
        db_column='id_utilisateur', related_name='prestataire'
    )
    description      = models.TextField(blank=True, null=True)
    photo_profil     = models.ImageField(
        upload_to='prestataires/photos/%Y/%m/',
        blank=True, null=True
    )
    est_premium      = models.BooleanField(default=False)
    est_verifie      = models.BooleanField(default=False)
    date_fin_premium = models.DateField(blank=True, null=True)
    note_moyenne     = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    badge_top        = models.BooleanField(default=False)
    nombre_avis      = models.IntegerField(default=0)
    est_actif        = models.BooleanField(default=True)
    est_disponible   = models.BooleanField(default=True)

    class Meta:
        db_table     = 'prestataire'
        verbose_name = 'Prestataire'
        verbose_name_plural = 'Prestataires'

    def __str__(self):
        return f"Prestataire : {self.id_utilisateur.prenoms} {self.id_utilisateur.nom}"

    @property
    def photo_url(self):
        if self.photo_profil:
            return self.photo_profil.url
        return None


# ──────────────────────────────────────────
#  Modèle FAVORI
# ──────────────────────────────────────────
class Favori(models.Model):

    id_favori      = models.AutoField(primary_key=True)
    id_client      = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        db_column='id_client',
        related_name='favoris'
    )
    id_prestataire = models.ForeignKey(
        Prestataire,
        on_delete=models.CASCADE,
        db_column='id_prestataire',
        related_name='mis_en_favori'
    )
    date_ajout     = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table     = 'favori'
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoris'
        # Un client ne peut pas mettre deux fois le même prestataire en favori
        unique_together = ('id_client', 'id_prestataire')
        ordering = ['-date_ajout']

    def __str__(self):
        return f"{self.id_client} ❤️ {self.id_prestataire}"


# ──────────────────────────────────────────
#  Modèle MESSAGE DE CONTACT
# ──────────────────────────────────────────
class MessageContact(models.Model):

    id_message_contact = models.AutoField(primary_key=True)
    prenom             = models.CharField(max_length=50)
    nom                = models.CharField(max_length=50)
    email              = models.EmailField(max_length=100)
    sujet              = models.CharField(max_length=100)
    message            = models.TextField()
    est_traite         = models.BooleanField(default=False)
    date_envoi         = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table     = 'message_contact'
        ordering     = ['-date_envoi']
        verbose_name = 'Message de contact'
        verbose_name_plural = 'Messages de contact'

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.sujet}"