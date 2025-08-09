from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Association, Membre, CarteMembre, InfoFizato, FonctionBureau, MembreBureau
import secrets
import string

@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = ['nom', 'date_creation', 'devise', 'created_at']
    search_fields = ['nom', 'devise', 'fondateurs']
    list_filter = ['date_creation', 'created_at']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'date_creation', 'devise')
        }),
        ('Détails', {
            'fields': ('fondateurs', 'description')
        }),
        ('Logos', {
            'fields': ('logo_association', 'logo_universite', 'logo_fizato')
        }),
        ('Métadonnées', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )

# Filtre personnalisé pour les comptes utilisateurs
class UserAccountFilter(admin.SimpleListFilter):
    title = 'Compte utilisateur'
    parameter_name = 'has_user'
    
    def lookups(self, request, model_admin):
        return (
            ('yes', 'A un compte'),
            ('no', 'Sans compte'),
        )
    
    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.filter(user__isnull=False)
        if self.value() == 'no':
            return queryset.filter(user__isnull=True)

@admin.register(Membre)
class MembreAdmin(admin.ModelAdmin):
    list_display = ['prenom', 'nom', 'numero_cin', 'association', 'filiere', 'numero_carte', 'has_user_account', 'created_at']
    list_filter = ['association', 'filiere', 'created_at', UserAccountFilter]
    search_fields = ['nom', 'prenom', 'numero_cin', 'numero_carte', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    actions = ['create_user_accounts', 'print_credentials']
    
    def has_user_account(self, obj):
        return obj.user is not None
    has_user_account.boolean = True
    has_user_account.short_description = 'Compte utilisateur'
    
    def create_user_accounts(self, request, queryset):
        """Action pour créer des comptes utilisateur pour les membres sélectionnés"""
        created_count = 0
        for membre in queryset:
            if not membre.user:
                # Générer un nom d'utilisateur unique
                username = f"{membre.prenom.lower()}.{membre.nom.lower()}"
                counter = 1
                original_username = username
                while User.objects.filter(username=username).exists():
                    username = f"{original_username}{counter}"
                    counter += 1
                
                # Générer un mot de passe aléatoire
                password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
                
                # Créer l'utilisateur
                user = User.objects.create_user(
                    username=username,
                    password=password,
                    first_name=membre.prenom,
                    last_name=membre.nom,
                    email=membre.email or ''
                )
                
                # Lier l'utilisateur au membre
                membre.user = user
                membre.save()
                created_count += 1
        
        self.message_user(request, f"{created_count} compte(s) utilisateur créé(s).")
    create_user_accounts.short_description = "Créer des comptes utilisateur"
    
    def print_credentials(self, request, queryset):
        """Action pour imprimer les identifiants des membres sélectionnés"""
        membres_with_users = queryset.filter(user__isnull=False)
        
        # Générer les mots de passe temporaires pour l'impression
        credentials_data = []
        for membre in membres_with_users:
            # Générer un nouveau mot de passe temporaire
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(8))
            membre.user.set_password(temp_password)
            membre.user.save()
            
            credentials_data.append({
                'membre': membre,
                'username': membre.user.username,
                'password': temp_password
            })
        
        # Rendre le template d'impression
        html_content = render_to_string('admin/print_credentials.html', {
            'credentials_data': credentials_data
        })
        
        response = HttpResponse(html_content, content_type='text/html')
        return response
    print_credentials.short_description = "Imprimer les identifiants"
    
    fieldsets = (
        ('Informations personnelles', {
            'fields': ('nom', 'prenom', 'numero_cin', 'date_naissance', 'photo')
        }),
        ('Association et formation', {
            'fields': ('association', 'filiere', 'parcours', 'etablissement')
        }),
        ('Contact', {
            'fields': ('telephone', 'email', 'nom_facebook', 'adresse')
        }),
        ('Carte membre', {
            'fields': ('numero_carte',)
        }),
        ('Compte utilisateur', {
            'fields': ('user',),
            'description': 'Associer ce membre à un compte utilisateur Django'
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )

@admin.register(CarteMembre)
class CarteMembreAdmin(admin.ModelAdmin):
    list_display = ['membre', 'numero_unique', 'date_generation', 'est_imprimee', 'date_impression']
    list_filter = ['est_imprimee', 'date_generation']
    search_fields = ['membre__nom', 'membre__prenom', 'numero_unique']
    readonly_fields = ['numero_unique', 'date_generation', 'date_impression']
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Si on modifie un objet existant
            return self.readonly_fields + ['membre']
        return self.readonly_fields


# ===============================
# PERSONNALISATION ADMIN USERS
# ===============================

class MembreInline(admin.StackedInline):
    model = Membre
    extra = 0
    readonly_fields = ['created_at', 'updated_at']
    
class CustomUserAdmin(BaseUserAdmin):
    """Administration personnalisée des utilisateurs avec lien vers Membre"""
    inlines = (MembreInline,)
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'has_membre', 'last_login']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    
    def has_membre(self, obj):
        try:
            return obj.membre is not None
        except:
            return False
    has_membre.boolean = True
    has_membre.short_description = 'A un profil membre'

# Désenregistrer l'admin User par défaut et enregistrer le nôtre
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(InfoFizato)
class InfoFizatoAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nom_complet', 'date_creation', 'created_at']
    search_fields = ['nom', 'nom_complet', 'devise', 'fondateurs']
    list_filter = ['date_creation', 'created_at']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = (
        ('Informations de base', {
            'fields': ('nom', 'nom_complet', 'date_creation')
        }),
        ('Contenu', {
            'fields': ('devise', 'fondateurs', 'description')
        }),
        ('Logo', {
            'fields': ('logo',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(FonctionBureau)
class FonctionBureauAdmin(admin.ModelAdmin):
    list_display = ['nom', 'niveau_hierarchique', 'description']
    search_fields = ['nom', 'description']
    list_filter = ['niveau_hierarchique']
    ordering = ['niveau_hierarchique', 'nom']


@admin.register(MembreBureau)
class MembreBureauAdmin(admin.ModelAdmin):
    list_display = ['membre', 'fonction', 'date_debut', 'date_fin', 'est_actuel']
    search_fields = ['membre__nom', 'membre__prenom', 'fonction__nom']
    list_filter = ['fonction', 'est_actuel', 'date_debut']
    ordering = ['fonction__niveau_hierarchique', 'membre__nom']
    autocomplete_fields = ['membre']
    
    fieldsets = (
        ('Assignation', {
            'fields': ('membre', 'fonction')
        }),
        ('Période de mandat', {
            'fields': ('date_debut', 'date_fin', 'est_actuel')
        })
    )


# Personnalisation du site admin
admin.site.site_header = "Administration FIZATO"
admin.site.site_title = "FIZATO Admin"
admin.site.index_title = "Gestion des Cartes Membres"
