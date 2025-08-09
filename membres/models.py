from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from django.contrib.auth.models import User
import uuid

class Association(models.Model):
    nom = models.CharField(max_length=200, verbose_name="Nom de l'Association")
    logo_association = models.ImageField(upload_to='logos/associations/', blank=True, null=True, verbose_name="Logo Association")
    logo_universite = models.ImageField(upload_to='logos/universites/', blank=True, null=True, verbose_name="Logo Université")
    logo_fizato = models.ImageField(upload_to='logos/fizato/', blank=True, null=True, verbose_name="Logo FI.ZA.TO")
    devise = models.CharField(max_length=500, verbose_name="Devise", blank=True, null=True)
    fondateurs = models.TextField(verbose_name="Fondateurs de l'association", default="", 
                                 help_text="Séparez les noms par des virgules")
    description = models.TextField(verbose_name="Description", blank=True, null=True)
    date_creation = models.DateField(verbose_name="Date de création", default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.nom
    
    def get_unique_code(self):
        """Génère un code unique de 2 lettres pour cette association"""
        # Récupérer toutes les lettres du nom de l'association
        letters = ''.join([char for char in self.nom.upper() if char.isalpha()])
        
        # Essayer d'abord les 2 premières lettres
        if len(letters) >= 2:
            code = letters[:2]
            # Vérifier si ce code est déjà utilisé par une autre association
            if not self._is_code_used_by_other_association(code):
                return code
        
        # Si le code des 2 premières lettres est pris, essayer avec d'autres combinaisons
        if len(letters) >= 3:
            # Essayer 1ère + 3ème lettre
            code = letters[0] + letters[2]
            if not self._is_code_used_by_other_association(code):
                return code
        
        if len(letters) >= 4:
            # Essayer 1ère + 4ème lettre
            code = letters[0] + letters[3]
            if not self._is_code_used_by_other_association(code):
                return code
                
            # Essayer 2ème + 4ème lettre
            code = letters[1] + letters[3]
            if not self._is_code_used_by_other_association(code):
                return code
        
        # Si toujours pas trouvé, utiliser l'ID de l'association
        return f"{letters[0] if letters else 'X'}{self.id % 100:01d}"
    
    def _is_code_used_by_other_association(self, code):
        """Vérifie si le code est déjà utilisé par une autre association"""
        from django.db.models import Q
        
        # Chercher tous les membres avec un numéro de carte se terminant par ce code
        # mais appartenant à une autre association
        existing_members = Membre.objects.filter(
            numero_carte__endswith=code
        ).exclude(association=self)
        
        return existing_members.exists()
    
    class Meta:
        verbose_name = "Association"
        verbose_name_plural = "Associations"

class Membre(models.Model):
    # Lien avec l'utilisateur Django (optionnel pour commencer)
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Utilisateur", help_text="Compte utilisateur associé")
    
    association = models.ForeignKey(Association, on_delete=models.CASCADE, related_name='membres')
    nom = models.CharField(max_length=100, verbose_name="Nom du membre")
    prenom = models.CharField(max_length=100, verbose_name="Prénom du membre")
    numero_cin = models.CharField(
        max_length=20, 
        verbose_name="N° CIN",
        unique=True,
        help_text="Numéro de Carte d'Identité Nationale"
    )
    filiere = models.CharField(max_length=100, verbose_name="Filière")
    parcours = models.CharField(max_length=100, verbose_name="Parcours")
    numero_carte = models.CharField(max_length=20, verbose_name="N°C", unique=True, blank=True)
    photo = models.ImageField(upload_to='photos/membres/', blank=True, null=True, verbose_name="Photo du membre")
    # Champs ajoutés pour la carte membre
    date_naissance = models.DateField(blank=True, null=True, verbose_name="Date de naissance")
    etablissement = models.CharField(max_length=150, blank=True, null=True, verbose_name="Établissement")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse ou Cité universitaire")
    telephone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    nom_facebook = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom Facebook")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Générer automatiquement le numéro de carte si pas défini
        if not self.numero_carte:
            # Obtenir le code unique de l'association (2 lettres)
            association_code = self.association.get_unique_code()
            
            # Compter le nombre de membres existants dans cette association
            count = Membre.objects.filter(association=self.association).count() + 1
            
            # Générer le numéro de carte : 0001 + code association (ex: 0001AE pour AERAF)
            self.numero_carte = f"{count:04d}{association_code}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"
    
    class Meta:
        verbose_name = "Membre"
        verbose_name_plural = "Membres"
        ordering = ['-created_at']

class CarteMembre(models.Model):
    membre = models.OneToOneField(Membre, on_delete=models.CASCADE, related_name='carte')
    numero_unique = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_generation = models.DateTimeField(auto_now_add=True)
    est_imprimee = models.BooleanField(default=False, verbose_name="Carte imprimée")
    date_impression = models.DateTimeField(blank=True, null=True, verbose_name="Date d'impression")
    
    def __str__(self):
        return f"Carte de {self.membre}"
    
    class Meta:
        verbose_name = "Carte Membre"
        verbose_name_plural = "Cartes Membres"
        ordering = ['-date_generation']


class InfoFizato(models.Model):
    """Informations sur l'organisation FIZATO"""
    nom = models.CharField(max_length=200, default="FI.ZA.TO", verbose_name="Nom de l'organisation")
    nom_complet = models.CharField(max_length=500, blank=True, null=True, verbose_name="Nom complet")
    date_creation = models.DateField(verbose_name="Date de création")
    devise = models.TextField(verbose_name="Devise", blank=True, null=True)
    fondateurs = models.TextField(verbose_name="Fondateurs", help_text="Séparez les noms par des virgules")
    description = models.TextField(verbose_name="Description")
    logo = models.ImageField(upload_to='logos/fizato/', blank=True, null=True, verbose_name="Logo FIZATO")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Information FIZATO"
        verbose_name_plural = "Informations FIZATO"


class FonctionBureau(models.Model):
    """Fonctions disponibles dans le bureau de FIZATO"""
    nom = models.CharField(max_length=100, verbose_name="Nom de la fonction")
    niveau_hierarchique = models.PositiveIntegerField(default=1, verbose_name="Niveau hiérarchique", 
                                                     help_text="1 = Président, 2 = Vice-président, etc.")
    description = models.TextField(blank=True, null=True, verbose_name="Description de la fonction")
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Fonction du Bureau"
        verbose_name_plural = "Fonctions du Bureau"
        ordering = ['niveau_hierarchique', 'nom']


class MembreBureau(models.Model):
    """Membres du bureau de FIZATO avec leurs fonctions"""
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, verbose_name="Membre")
    fonction = models.ForeignKey(FonctionBureau, on_delete=models.CASCADE, verbose_name="Fonction")
    date_debut = models.DateField(verbose_name="Date de début de mandat")
    date_fin = models.DateField(blank=True, null=True, verbose_name="Date de fin de mandat")
    est_actuel = models.BooleanField(default=True, verbose_name="Mandat actuel")
    mandat = models.ForeignKey('Mandat', on_delete=models.CASCADE, null=True, blank=True, related_name='membres_bureau')
    
    def __str__(self):
        return f"{self.membre} - {self.fonction}"
    
    class Meta:
        verbose_name = "Membre du Bureau"
        verbose_name_plural = "Membres du Bureau"
        ordering = ['fonction__niveau_hierarchique', 'membre__nom']
        # Retirer unique_together pour permettre plusieurs membres par fonction
        # Mais garder l'unicité pour membre + fonction + mandat actuel
        constraints = [
            models.UniqueConstraint(
                fields=['membre', 'fonction'],
                condition=models.Q(est_actuel=True),
                name='unique_membre_fonction_actuel'
            )
        ]


class Mandat(models.Model):
    """Modèle pour gérer les mandats et l'historique des bureaux"""
    nom = models.CharField(max_length=100, help_text="Ex: Mandat 2024-2026")
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True, verbose_name="Date de fin")
    est_actuel = models.BooleanField(default=False)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_debut']
        constraints = [
            models.UniqueConstraint(
                fields=['est_actuel'],
                condition=models.Q(est_actuel=True),
                name='unique_mandat_actuel'
            )
        ]
    
    def __str__(self):
        return self.nom
    
    def terminer_mandat(self):
        """Termine le mandat actuel et archive tous les membres du bureau"""
        if self.est_actuel:
            # Archiver tous les membres du bureau actuel
            MembreBureau.objects.filter(est_actuel=True).update(
                est_actuel=False,
                date_fin=timezone.now().date()
            )
            
            # Marquer le mandat comme terminé
            self.est_actuel = False
            self.save()


class ComiteDoyen(models.Model):
    """Modèle pour les membres du comité des doyens"""
    membre = models.ForeignKey(Membre, on_delete=models.CASCADE, related_name='comite_doyen')
    titre = models.CharField(max_length=100, default="Membre du Comité des Doyens")
    date_nomination = models.DateField(default=timezone.now)
    date_fin = models.DateField(null=True, blank=True)
    est_actif = models.BooleanField(default=True)
    ordre_affichage = models.IntegerField(default=1)
    mandat = models.ForeignKey(Mandat, on_delete=models.CASCADE, null=True, blank=True, related_name='comite_doyen')
    
    class Meta:
        ordering = ['ordre_affichage', 'date_nomination']
    
    def __str__(self):
        return f"{self.membre.prenom} {self.membre.nom} - {self.titre}"
