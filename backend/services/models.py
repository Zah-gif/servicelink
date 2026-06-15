from django.db import models


# ──────────────────────────────────────────
#  Modèle CATEGORIE
# ──────────────────────────────────────────
class Categorie(models.Model):

    id_categorie  = models.AutoField(primary_key=True)
    nom_categorie = models.CharField(max_length=50, unique=True)
    icone         = models.CharField(max_length=100, blank=True, null=True)
    est_active    = models.BooleanField(default=True)

    class Meta:
        db_table     = 'categorie'
        ordering     = ['nom_categorie']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom_categorie


# ──────────────────────────────────────────
#  Modèle METIER
# ──────────────────────────────────────────
class Metier(models.Model):

    id_metier    = models.AutoField(primary_key=True)
    id_categorie = models.ForeignKey(
        Categorie,
        on_delete=models.RESTRICT,
        db_column='id_categorie',
        related_name='metiers'
    )
    nom_metier   = models.CharField(max_length=80)
    est_actif    = models.BooleanField(default=True)

    class Meta:
        db_table     = 'metier'
        ordering     = ['nom_metier']
        verbose_name = 'Métier'
        verbose_name_plural = 'Métiers'

    def __str__(self):
        return f"{self.nom_metier} ({self.id_categorie.nom_categorie})"


# ──────────────────────────────────────────
#  Modèle COMMUNE
# ──────────────────────────────────────────
class Commune(models.Model):

    id_commune  = models.AutoField(primary_key=True)
    nom_commune = models.CharField(max_length=50, unique=True)
    latitude    = models.DecimalField(max_digits=10, decimal_places=7,
                                      blank=True, null=True)
    longitude   = models.DecimalField(max_digits=10, decimal_places=7,
                                      blank=True, null=True)

    class Meta:
        db_table     = 'commune'
        ordering     = ['nom_commune']
        verbose_name = 'Commune'
        verbose_name_plural = 'Communes'

    def __str__(self):
        return self.nom_commune


# ──────────────────────────────────────────
#  Modèle SERVICE
# ──────────────────────────────────────────
class Service(models.Model):

    id_service     = models.AutoField(primary_key=True)
    id_prestataire = models.ForeignKey(
        'users.Prestataire',
        on_delete=models.CASCADE,
        db_column='id_prestataire',
        related_name='services'
    )
    id_metier      = models.ForeignKey(
        Metier,
        on_delete=models.RESTRICT,
        db_column='id_metier',
        related_name='services'
    )
    id_categorie   = models.ForeignKey(
        Categorie,
        on_delete=models.RESTRICT,
        db_column='id_categorie',
        related_name='services'
    )
    titre          = models.CharField(max_length=100)
    description    = models.TextField(blank=True, null=True)

    # ── Plage de prix ──
    tarif_min      = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        help_text='Prix minimum en FCFA'
    )
    tarif_max      = models.DecimalField(
        max_digits=10, decimal_places=2,
        blank=True, null=True,
        help_text='Prix maximum en FCFA'
    )

    # ── Plage de durée (en minutes) ──
    duree_min      = models.IntegerField(
        blank=True, null=True,
        help_text='Durée minimum en minutes'
    )
    duree_max      = models.IntegerField(
        blank=True, null=True,
        help_text='Durée maximum en minutes'
    )

    est_actif      = models.BooleanField(default=True)
    date_creation  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table     = 'service'
        ordering     = ['-date_creation']
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

    def __str__(self):
        return f"{self.titre} — {self.id_prestataire}"

    @property
    def tarif_affiche(self):
        """Retourne la plage de prix formatée"""
        if self.tarif_min and self.tarif_max:
            return f"{int(self.tarif_min):,} — {int(self.tarif_max):,} FCFA"
        elif self.tarif_min:
            return f"À partir de {int(self.tarif_min):,} FCFA"
        elif self.tarif_max:
            return f"Jusqu'à {int(self.tarif_max):,} FCFA"
        return "Prix sur devis"

    @property
    def duree_affichee(self):
        """Retourne la plage de durée formatée"""
        if self.duree_min and self.duree_max:
            return f"{self.duree_min} — {self.duree_max} min"
        elif self.duree_min:
            return f"À partir de {self.duree_min} min"
        elif self.duree_max:
            return f"Jusqu'à {self.duree_max} min"
        return None