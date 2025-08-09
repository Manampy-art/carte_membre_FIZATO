from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Q
from .models import Association, Membre, CarteMembre, InfoFizato, FonctionBureau, MembreBureau, Mandat, ComiteDoyen
from .forms import AssociationForm, MembreForm, GenerationCarteForm, MembreAutoEditForm, InfoFizatoForm, FonctionBureauForm, MembreBureauForm, MandatForm, CreerMandatForm, ComiteDoyenForm
from .decorators import admin_required, can_modify_members, can_view_member_data

@login_required
def dashboard(request):
    """Vue principale avec statistiques"""
    context = {
        'total_associations': Association.objects.count(),
        'total_membres': Membre.objects.count(),
        'total_cartes': CarteMembre.objects.count(),
        'cartes_imprimees': CarteMembre.objects.filter(est_imprimee=True).count(),
    }
    return render(request, 'membres/dashboard.html', context)

@login_required
def liste_associations(request):
    """Liste des associations avec statistiques"""
    associations = Association.objects.prefetch_related('membres').all()
    total_membres = Membre.objects.count()
    
    context = {
        'associations': associations,
        'total_membres': total_membres,
        'is_admin': request.user.is_staff or request.user.is_superuser
    }
    return render(request, 'membres/liste_associations.html', context)

def detail_association(request, association_id):
    """Détail d'une association avec ses membres"""
    association = get_object_or_404(Association, id=association_id)
    membres = association.membres.all().order_by('-created_at')
    
    context = {
        'association': association,
        'membres': membres,
    }
    return render(request, 'membres/detail_association.html', context)

@can_modify_members
def ajouter_association(request):
    """Ajouter une nouvelle association"""
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES)
        if form.is_valid():
            association = form.save()
            messages.success(request, f'Association "{association.nom}" ajoutée avec succès!')
            return redirect('liste_associations')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de l\'association. Vérifiez les données.')
    else:
        form = AssociationForm()
    
    return render(request, 'membres/ajouter_association.html', {'form': form})

@can_modify_members
def modifier_association(request, association_id):
    """Modifier une association existante"""
    association = get_object_or_404(Association, id=association_id)
    
    if request.method == 'POST':
        form = AssociationForm(request.POST, request.FILES, instance=association)
        if form.is_valid():
            association = form.save()
            messages.success(request, f'Association "{association.nom}" modifiée avec succès!')
            return redirect('liste_associations')
        else:
            messages.error(request, 'Erreur lors de la modification de l\'association.')
    else:
        form = AssociationForm(instance=association)
    
    return render(request, 'membres/ajouter_association.html', {
        'form': form, 
        'association': association,
        'edit_mode': True
    })

@can_modify_members
def supprimer_association(request, association_id):
    """Supprimer une association"""
    association = get_object_or_404(Association, id=association_id)
    
    if request.method == 'POST':
        nom_association = association.nom
        association.delete()
        messages.success(request, f'Association "{nom_association}" supprimée avec succès!')
        return redirect('liste_associations')
    
    return render(request, 'membres/confirmer_suppression_association.html', {
        'association': association
    })

def liste_membres(request):
    """Liste des membres - tous les utilisateurs connectés peuvent voir tous les membres"""
    # Tous les utilisateurs connectés peuvent voir la liste complète des membres
    membres = Membre.objects.select_related('association').prefetch_related('carte')
    
    return render(request, 'membres/liste_membres.html', {
        'membres': membres,
        'is_admin': request.user.is_staff or request.user.is_superuser
    })

@can_modify_members
def ajouter_membre(request, association_id=None):
    """Ajouter un nouveau membre"""
    association = None
    if association_id:
        association = get_object_or_404(Association, id=association_id)
    
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES, association_id=association_id)
        if form.is_valid():
            membre = form.save()
            messages.success(request, f'Membre "{membre.prenom} {membre.nom}" ajouté avec succès!')
            if association:
                return redirect('detail_association', association_id=association.id)
            else:
                return redirect('liste_membres')
        else:
            messages.error(request, 'Erreur lors de l\'ajout du membre. Vérifiez les données.')
    else:
        form = MembreForm(association_id=association_id)
    
    context = {
        'form': form,
        'association': association,
        'is_edit': False,
    }
    return render(request, 'membres/ajouter_membre.html', context)

@can_modify_members
def modifier_membre(request, membre_id):
    """Modifier un membre existant (réservé aux administrateurs)"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    if request.method == 'POST':
        form = MembreForm(request.POST, request.FILES, instance=membre)
        if form.is_valid():
            try:
                membre_instance = form.save()
                messages.success(request, f'Membre "{membre_instance.prenom} {membre_instance.nom}" modifié avec succès!')
                return redirect('liste_membres')
            except Exception as e:
                messages.error(request, f'Erreur lors de la sauvegarde : {str(e)}')
        else:
            # Afficher les erreurs spécifiques du formulaire
            messages.error(request, 'Erreur dans le formulaire. Veuillez vérifier les champs marqués en rouge.')
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_label}: {error}')
    else:
        form = MembreForm(instance=membre)
    
    return render(request, 'membres/modifier_membre.html', {
        'form': form, 
        'membre': membre,
        'is_edit': True,
    })

@can_modify_members
def supprimer_membre(request, membre_id):
    """Supprimer un membre"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    if request.method == 'POST':
        nom_membre = f"{membre.prenom} {membre.nom}"
        membre.delete()
        messages.success(request, f'Membre "{nom_membre}" supprimé avec succès!')
        return redirect('liste_membres')
    
    return render(request, 'membres/supprimer_membre.html', {
        'membre': membre
    })

@can_modify_members
def generer_cartes(request):
    """Sélectionner les membres pour générer leurs cartes"""
    if request.method == 'POST':
        membres_ids = request.POST.getlist('membres')
        
        if membres_ids:
            # Limiter à 20 membres maximum par page
            if len(membres_ids) > 20:
                messages.error(request, 'Vous ne pouvez sélectionner que 20 membres maximum par page d\'impression.')
                return redirect('generer_cartes')
            
            # Rediriger vers la page d'impression multiple
            membres_ids_str = ','.join(membres_ids)
            return redirect('print_cartes_multiples', membres_ids=membres_ids_str)
        else:
            messages.error(request, 'Veuillez sélectionner au moins un membre.')
    
    # Récupérer tous les membres de toutes les associations FIZATO
    membres = Membre.objects.select_related('association').all().order_by('association__nom', 'nom', 'prenom')
    associations = Association.objects.all().order_by('nom')
    
    context = {
        'membres': membres,
        'associations': associations,
    }
    return render(request, 'membres/generer_cartes.html', context)

def liste_cartes_membres(request):
    """Liste des cartes - tous les utilisateurs connectés peuvent voir toutes les cartes"""
    # Tous les utilisateurs connectés peuvent voir toutes les cartes
    cartes = CarteMembre.objects.select_related('membre__association').all()
    
    return render(request, 'membres/liste_cartes_membres.html', {
        'cartes': cartes,
        'is_admin': request.user.is_staff or request.user.is_superuser
    })

def print_carte_membre(request, membre_id):
    """Imprimer la carte d'un membre spécifique"""
    membre = get_object_or_404(Membre, id=membre_id)
    
    # Créer une carte si elle n'existe pas
    carte, created = CarteMembre.objects.get_or_create(
        membre=membre,
        defaults={'est_imprimee': False}
    )
    
    # Marquer comme imprimée et mettre à jour la date d'impression
    if not carte.est_imprimee:
        carte.est_imprimee = True
        carte.date_impression = timezone.now()
        carte.save()
    
    context = {
        'membre': membre,
        'carte': carte,
    }
    
    return render(request, 'membres/print_carte_membre.html', context)

def print_cartes_multiples(request, membres_ids):
    """Imprimer plusieurs cartes sur une page (format 4x5 = 20 cartes max)"""
    # Convertir la chaîne d'IDs en liste
    try:
        ids_list = [int(id.strip()) for id in membres_ids.split(',') if id.strip()]
    except ValueError:
        messages.error(request, 'Erreur dans les identifiants des membres.')
        return redirect('generer_cartes')
    
    # Limiter à 20 membres maximum
    if len(ids_list) > 20:
        messages.error(request, 'Maximum 20 cartes par page d\'impression.')
        return redirect('generer_cartes')
    
    # Récupérer les membres
    membres = Membre.objects.filter(id__in=ids_list).select_related('association')
    
    if not membres.exists():
        messages.error(request, 'Aucun membre trouvé avec ces identifiants.')
        return redirect('generer_cartes')
    
    # Créer les cartes si elles n'existent pas et les marquer comme imprimées
    cartes_crees = 0
    for membre in membres:
        carte, created = CarteMembre.objects.get_or_create(
            membre=membre,
            defaults={'est_imprimee': True, 'date_impression': timezone.now()}
        )
        if created:
            cartes_crees += 1
        elif not carte.est_imprimee:
            carte.est_imprimee = True
            carte.date_impression = timezone.now()
            carte.save()
    
    context = {
        'membres': membres,
        'total_cartes': membres.count(),
        'cartes_crees': cartes_crees,
    }
    
    return render(request, 'membres/print_cartes_multiples.html', context)


# ===============================
# VUES D'AUTHENTIFICATION
# ===============================

def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.get_full_name() or user.username} !')
            
            # Rediriger vers la page demandée ou dashboard
            next_page = request.GET.get('next', 'dashboard')
            return redirect(next_page)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'membres/auth/login.html')

def logout_view(request):
    """Vue de déconnexion"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('login')

@login_required
def profile_view(request):
    """Vue du profil utilisateur"""
    try:
        membre = request.user.membre
    except:
        membre = None
    
    context = {
        'membre': membre,
    }
    return render(request, 'membres/auth/profile.html', context)

@login_required
def change_password_view(request):
    """Vue pour changer le mot de passe"""
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        if not request.user.check_password(current_password):
            messages.error(request, 'Mot de passe actuel incorrect.')
        elif new_password != confirm_password:
            messages.error(request, 'Les nouveaux mots de passe ne correspondent pas.')
        elif len(new_password) < 8:
            messages.error(request, 'Le mot de passe doit contenir au moins 8 caractères.')
        else:
            request.user.set_password(new_password)
            request.user.save()
            messages.success(request, 'Mot de passe modifié avec succès. Veuillez vous reconnecter.')
            logout(request)
            return redirect('login')
    
    return render(request, 'membres/auth/change_password.html')

@login_required
def modifier_mes_informations(request):
    """Permettre à un utilisateur de modifier ses propres informations de membre"""
    try:
        # Vérifier si l'utilisateur a un profil membre associé
        membre = request.user.membre
    except:
        messages.error(request, 'Aucun profil membre associé à votre compte.')
        return redirect('profile')
    
    if request.method == 'POST':
        # Utiliser le formulaire spécialisé pour l'auto-modification
        form = MembreAutoEditForm(request.POST, request.FILES, instance=membre)
        
        if form.is_valid():
            # Sauvegarder les modifications
            try:
                form.save()
                messages.success(request, 'Vos informations ont été mises à jour avec succès!')
                return redirect('profile')
            except Exception as e:
                messages.error(request, f'Erreur lors de la sauvegarde : {str(e)}')
        else:
            # Afficher les erreurs spécifiques du formulaire
            for field, errors in form.errors.items():
                for error in errors:
                    field_label = form.fields[field].label if field in form.fields else field
                    messages.error(request, f'{field_label}: {error}')
    else:
        # Utiliser le formulaire spécialisé avec l'instance du membre
        form = MembreAutoEditForm(instance=membre)
    
    return render(request, 'membres/modifier_mes_informations.html', {
        'form': form,
        'membre': membre,
        'is_edit': True,
    })


# ================================
# VUES POUR FIZATO
# ================================

@login_required
def detail_fizato(request):
    """Page de détails de l'organisation FIZATO"""
    try:
        info_fizato = InfoFizato.objects.first()
    except InfoFizato.DoesNotExist:
        info_fizato = None
    
    # Récupérer les membres du bureau actuels
    membres_bureau = MembreBureau.objects.filter(est_actuel=True).order_by('fonction__niveau_hierarchique', 'membre__nom')
    
    # Récupérer toutes les fonctions pour l'organigramme
    fonctions = FonctionBureau.objects.all().order_by('niveau_hierarchique', 'nom')
    
    # Comité des doyens
    comite_doyen = ComiteDoyen.objects.filter(est_actif=True).select_related('membre').order_by('ordre_affichage', 'date_nomination')
    
    # Mandat actuel
    mandat_actuel = Mandat.objects.filter(est_actuel=True).first()
    
    # Compter les statistiques
    total_associations = Association.objects.count()
    total_membres = Membre.objects.count()
    total_cartes = CarteMembre.objects.count()
    
    context = {
        'info_fizato': info_fizato,
        'membres_bureau': membres_bureau,
        'fonctions': fonctions,
        'comite_doyen': comite_doyen,
        'mandat_actuel': mandat_actuel,
        'total_associations': total_associations,
        'total_membres': total_membres,
        'total_cartes': total_cartes,
    }
    
    return render(request, 'membres/detail_fizato.html', context)


@admin_required
def modifier_fonction_bureau(request, fonction_id):
    """Modifier une fonction du bureau"""
    fonction = get_object_or_404(FonctionBureau, id=fonction_id)
    
    if request.method == 'POST':
        form = FonctionBureauForm(request.POST, instance=fonction)
        if form.is_valid():
            form.save()
            messages.success(request, f'La fonction "{fonction.nom}" a été modifiée avec succès.')
            return redirect('detail_fizato')
    else:
        form = FonctionBureauForm(instance=fonction)
    
    return render(request, 'membres/ajouter_fonction_bureau.html', {
        'form': form,
        'fonction': fonction,
        'is_edit': True,
    })


@admin_required
def supprimer_fonction_bureau(request, fonction_id):
    """Supprimer une fonction du bureau"""
    fonction = get_object_or_404(FonctionBureau, id=fonction_id)
    
    # Vérifier si la fonction est utilisée
    if MembreBureau.objects.filter(fonction=fonction, est_actuel=True).exists():
        messages.error(request, f'Impossible de supprimer la fonction "{fonction.nom}" car elle est actuellement assignée à des membres.')
        return redirect('detail_fizato')
    
    if request.method == 'POST':
        nom_fonction = fonction.nom
        fonction.delete()
        messages.success(request, f'La fonction "{nom_fonction}" a été supprimée avec succès.')
        return redirect('detail_fizato')
    
    return render(request, 'membres/confirmer_suppression_fonction.html', {
        'fonction': fonction,
    })


@admin_required
def terminer_mandat(request):
    """Terminer le mandat actuel et archiver tous les membres du bureau"""
    mandat_actuel = Mandat.objects.filter(est_actuel=True).first()
    
    if request.method == 'POST':
        if mandat_actuel:
            # Archiver tous les membres du bureau actuel
            MembreBureau.objects.filter(est_actuel=True).update(
                est_actuel=False,
                date_fin=timezone.now().date()
            )
            
            # Marquer le mandat comme terminé
            mandat_actuel.est_actuel = False
            mandat_actuel.save()
            
            messages.success(request, f'Le mandat "{mandat_actuel.nom}" a été terminé et tous les membres ont été archivés.')
        else:
            messages.warning(request, 'Aucun mandat actuel trouvé.')
        
        return redirect('detail_fizato')
    
    return render(request, 'membres/confirmer_terminer_mandat.html', {
        'mandat_actuel': mandat_actuel,
        'membres_bureau': MembreBureau.objects.filter(est_actuel=True).select_related('membre', 'fonction'),
    })


@admin_required
def terminer_mandat_bureau(request):
    """Terminer automatiquement le mandat actuel et créer un nouveau mandat"""
    mandat_actuel = Mandat.objects.filter(est_actuel=True).first()
    
    if not mandat_actuel:
        messages.error(request, 'Aucun mandat actuel trouvé.')
        return redirect('detail_fizato')
    
    membres_bureau = MembreBureau.objects.filter(est_actuel=True).select_related('membre', 'fonction', 'membre__association')
    comite_doyen = ComiteDoyen.objects.filter(est_actif=True).select_related('membre', 'membre__association')
    
    if request.method == 'POST':
        # Automatiser le processus complet
        date_fin = timezone.now().date()
        
        # 1. Terminer le mandat actuel
        mandat_actuel.est_actuel = False
        mandat_actuel.date_fin = date_fin
        mandat_actuel.motif_fin = "Fin de mandat - Transition automatique"
        mandat_actuel.save()
        
        # 2. Archiver tous les membres du bureau actuel
        nb_bureau_archives = 0
        for membre_bureau in membres_bureau:
            membre_bureau.est_actuel = False
            membre_bureau.date_fin = date_fin
            membre_bureau.mandat = mandat_actuel
            membre_bureau.save()
            nb_bureau_archives += 1
        
        # 3. Archiver tous les membres du comité des doyens
        nb_doyen_archives = 0
        for doyen in comite_doyen:
            doyen.est_actif = False
            doyen.date_fin = date_fin
            doyen.mandat = mandat_actuel
            doyen.save()
            nb_doyen_archives += 1
        
        # 4. Créer automatiquement le nouveau mandat
        from datetime import date
        annee_actuelle = date_fin.year
        nouveau_nom = f"{annee_actuelle + 1}-{annee_actuelle + 2}"
        
        nouveau_mandat = Mandat.objects.create(
            nom=nouveau_nom,
            description=f"Mandat automatiquement créé après la fin du mandat {mandat_actuel.nom}",
            date_debut=date_fin,
            est_actuel=True
        )
        
        messages.success(
            request, 
            f'✅ Mandat "{mandat_actuel.nom}" terminé et archivé.<br>'
            f'📋 {nb_bureau_archives} membres du bureau archivés.<br>'
            f'👥 {nb_doyen_archives} membres du comité des doyens archivés.<br>'
            f'🆕 Nouveau mandat "{nouveau_mandat.nom}" créé et activé.<br>'
            f'➡️ Vous pouvez maintenant constituer le nouveau bureau.'
        )
        return redirect('detail_fizato')
    
    # Afficher la page de confirmation
    return render(request, 'membres/confirmer_terminer_mandat_bureau.html', {
        'mandat_actuel': mandat_actuel,
        'membres_bureau': membres_bureau,
        'comite_doyen': comite_doyen,
    })


@admin_required
def creer_mandat(request):
    """Créer un nouveau mandat"""
    if request.method == 'POST':
        form = CreerMandatForm(request.POST)
        if form.is_valid():
            # Marquer tous les autres mandats comme non actuels
            Mandat.objects.all().update(est_actuel=False)
            
            # Créer le nouveau mandat (sans date de fin par défaut)
            mandat = form.save(commit=False)
            mandat.est_actuel = True
            mandat.save()
            
            messages.success(request, f'Le nouveau mandat "{mandat.nom}" a été créé avec succès.')
            return redirect('detail_fizato')
    else:
        form = CreerMandatForm()
    
    return render(request, 'membres/creer_mandat.html', {
        'form': form,
    })


@login_required
def historique_fizato(request):
    """Afficher l'historique des mandats et des bureaux (tous les mandats)"""
    # Récupérer tous les mandats, triés par ordre chronologique
    # 1. Mandat actuel en premier (s'il existe)
    # 2. Puis mandats terminés par date de fin décroissante (plus récent en premier)
    from django.db.models import Case, When, Value, IntegerField
    
    mandats = Mandat.objects.annotate(
        tri_ordre=Case(
            When(est_actuel=True, then=Value(0)),  # Mandat actuel en premier
            default=Value(1),  # Mandats terminés ensuite
            output_field=IntegerField()
        )
    ).order_by('tri_ordre', '-date_fin', '-date_debut')
    
    # Ajouter les membres du bureau et du comité des doyens pour chaque mandat
    for mandat in mandats:
        if mandat.est_actuel:
            # Pour le mandat actuel, prendre les membres actuels
            mandat.membres_bureau_archive = MembreBureau.objects.filter(
                est_actuel=True
            ).select_related('membre', 'fonction', 'membre__association').order_by('fonction__niveau_hierarchique', 'membre__nom')
            
            mandat.comite_doyen_archive = ComiteDoyen.objects.filter(
                est_actif=True
            ).select_related('membre', 'membre__association').order_by('ordre_affichage', 'membre__nom')
        else:
            # Pour les anciens mandats, prendre uniquement les membres explicitement liés à ce mandat
            mandat.membres_bureau_archive = MembreBureau.objects.filter(
                mandat=mandat,
                est_actuel=False
            ).select_related('membre', 'fonction', 'membre__association').order_by('fonction__niveau_hierarchique', 'membre__nom')
            
            # Ajouter les membres du comité des doyens de ce mandat
            mandat.comite_doyen_archive = ComiteDoyen.objects.filter(
                mandat=mandat,
                est_actif=False
            ).select_related('membre', 'membre__association').order_by('ordre_affichage', 'membre__nom')
    
    # Calculer les statistiques
    total_mandats = mandats.count()
    mandats_actuels = mandats.filter(est_actuel=True).count()
    mandats_archives = mandats.filter(est_actuel=False).count()
    
    # Calculer approximativement le nombre de membres total dans l'historique
    total_membres_historique = 0
    for mandat in mandats:
        if mandat.est_actuel:
            total_membres_historique += MembreBureau.objects.filter(est_actuel=True).count()
            total_membres_historique += ComiteDoyen.objects.filter(est_actif=True).count()
        else:
            total_membres_historique += MembreBureau.objects.filter(mandat=mandat, est_actuel=False).count()
            total_membres_historique += ComiteDoyen.objects.filter(mandat=mandat, est_actif=False).count()

    context = {
        'mandats': mandats,
        'total_mandats': total_mandats,
        'mandats_actuels': mandats_actuels,
        'mandats_archives': mandats_archives,
        'total_membres_historique': total_membres_historique,
    }
    
    return render(request, 'membres/historique_fizato.html', context)


@admin_required
def vider_historique(request):
    """Vider tout l'historique (supprimer tous les mandats terminés et leurs données)"""
    if request.method == 'POST':
        # Supprimer tous les mandats terminés et leurs relations
        mandats_termines = Mandat.objects.filter(est_actuel=False)
        count_mandats = mandats_termines.count()
        
        # Supprimer tous les MembreBureau et ComiteDoyen liés aux mandats terminés
        count_bureau = MembreBureau.objects.filter(mandat__in=mandats_termines).count()
        count_comite = ComiteDoyen.objects.filter(mandat__in=mandats_termines).count()
        
        # Supprimer aussi les MembreBureau et ComiteDoyen archivés sans mandat
        count_bureau += MembreBureau.objects.filter(est_actuel=False, mandat__isnull=True).count()
        count_comite += ComiteDoyen.objects.filter(est_actif=False, mandat__isnull=True).count()
        
        # Effectuer les suppressions
        MembreBureau.objects.filter(mandat__in=mandats_termines).delete()
        ComiteDoyen.objects.filter(mandat__in=mandats_termines).delete()
        MembreBureau.objects.filter(est_actuel=False, mandat__isnull=True).delete()
        ComiteDoyen.objects.filter(est_actif=False, mandat__isnull=True).delete()
        mandats_termines.delete()
        
        messages.success(
            request, 
            f'Historique vidé avec succès ! '
            f'{count_mandats} mandat(s), {count_bureau} membre(s) du bureau et {count_comite} membre(s) du comité des doyens supprimés.'
        )
    
    return redirect('historique_fizato')


@admin_required
def supprimer_mandat_archive(request, mandat_id):
    """Supprimer un mandat archivé spécifique et toutes ses données"""
    if request.method == 'POST':
        try:
            mandat = get_object_or_404(Mandat, id=mandat_id, est_actuel=False)
            
            # Compter les éléments à supprimer
            count_bureau = MembreBureau.objects.filter(mandat=mandat).count()
            count_comite = ComiteDoyen.objects.filter(mandat=mandat).count()
            
            # Supprimer les données liées
            MembreBureau.objects.filter(mandat=mandat).delete()
            ComiteDoyen.objects.filter(mandat=mandat).delete()
            
            # Supprimer le mandat
            nom_mandat = mandat.nom
            mandat.delete()
            
            messages.success(
                request, 
                f'Archive "{nom_mandat}" supprimée avec succès ! '
                f'{count_bureau} membre(s) du bureau et {count_comite} membre(s) du comité des doyens supprimés.'
            )
        except Exception as e:
            messages.error(request, f'Erreur lors de la suppression : {str(e)}')
    
    return redirect('historique_fizato')


@admin_required
def ajouter_comite_doyen(request):
    """Ajouter un membre au comité des doyens"""
    if request.method == 'POST':
        form = ComiteDoyenForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Membre ajouté au comité des doyens avec succès.')
            return redirect('detail_fizato')
    else:
        form = ComiteDoyenForm()
    
    return render(request, 'membres/ajouter_comite_doyen.html', {
        'form': form,
    })


@admin_required
def supprimer_comite_doyen(request, doyen_id):
    """Retirer un membre du comité des doyens"""
    doyen = get_object_or_404(ComiteDoyen, id=doyen_id)
    
    if request.method == 'POST':
        nom_membre = f"{doyen.membre.prenom} {doyen.membre.nom}"
        doyen.delete()
        messages.success(request, f'{nom_membre} a été retiré du comité des doyens.')
        return redirect('detail_fizato')
    
    return render(request, 'membres/confirmer_suppression_doyen.html', {
        'doyen': doyen,
    })


@admin_required
def ajouter_info_fizato(request):
    """Ajouter ou modifier les informations de FIZATO"""
    try:
        info_fizato = InfoFizato.objects.first()
    except InfoFizato.DoesNotExist:
        info_fizato = None
    
    if request.method == 'POST':
        form = InfoFizatoForm(request.POST, request.FILES, instance=info_fizato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Les informations de FIZATO ont été sauvegardées avec succès!')
            return redirect('detail_fizato')
        else:
            messages.error(request, 'Erreur lors de la sauvegarde. Vérifiez les champs.')
    else:
        form = InfoFizatoForm(instance=info_fizato)
    
    return render(request, 'membres/ajouter_info_fizato.html', {
        'form': form,
        'info_fizato': info_fizato,
        'is_edit': info_fizato is not None
    })


@admin_required
def ajouter_fonction_bureau(request):
    """Ajouter une nouvelle fonction au bureau"""
    if request.method == 'POST':
        form = FonctionBureauForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La fonction a été ajoutée avec succès!')
            return redirect('detail_fizato')
        else:
            messages.error(request, 'Erreur lors de l\'ajout de la fonction.')
    else:
        form = FonctionBureauForm()
    
    return render(request, 'membres/ajouter_fonction_bureau.html', {
        'form': form
    })


@admin_required
def ajouter_membre_bureau(request):
    """Ajouter un membre au bureau avec sa fonction"""
    if request.method == 'POST':
        form = MembreBureauForm(request.POST)
        if form.is_valid():
            fonction = form.cleaned_data['fonction']
            est_actuel = form.cleaned_data['est_actuel']
            
            if est_actuel:
                # Vérifier si c'est pour la fonction de Président
                if fonction.nom.lower() == 'président':
                    # Pour le Président, il ne peut y en avoir qu'un seul
                    anciens_presidents = MembreBureau.objects.filter(
                        fonction=fonction, 
                        est_actuel=True
                    )
                    if anciens_presidents.exists():
                        # Désactiver l'ancien président
                        anciens_presidents.update(est_actuel=False)
                        messages.info(request, f'L\'ancien président a été remplacé par {form.cleaned_data["membre"]}.')
                else:
                    # Pour les autres fonctions, on peut avoir plusieurs personnes
                    # Pas besoin de désactiver les anciens
                    pass
            
            form.save()
            messages.success(request, 'Le membre a été ajouté au bureau avec succès!')
            return redirect('detail_fizato')
        else:
            messages.error(request, 'Erreur lors de l\'ajout du membre au bureau.')
    else:
        form = MembreBureauForm()
    
    return render(request, 'membres/ajouter_membre_bureau.html', {
        'form': form
    })


@admin_required
def supprimer_membre_bureau(request, membre_bureau_id):
    """Supprimer un membre du bureau"""
    membre_bureau = get_object_or_404(MembreBureau, id=membre_bureau_id)
    
    if request.method == 'POST':
        nom_membre = str(membre_bureau.membre)
        fonction = str(membre_bureau.fonction)
        membre_bureau.delete()
        messages.success(request, f'{nom_membre} a été retiré de la fonction {fonction}.')
        return redirect('detail_fizato')
    
    return render(request, 'membres/confirmer_suppression_membre_bureau.html', {
        'membre_bureau': membre_bureau
    })


@login_required
def detail_membre_bureau(request, membre_bureau_id):
    """Afficher les détails d'un membre du bureau"""
    membre_bureau = get_object_or_404(MembreBureau, id=membre_bureau_id)
    
    return render(request, 'membres/detail_membre_bureau.html', {
        'membre_bureau': membre_bureau
    })
