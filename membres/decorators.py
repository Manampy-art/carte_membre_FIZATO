from django.http import HttpResponseForbidden
from django.shortcuts import render
from functools import wraps
from django.contrib.auth.decorators import login_required

def admin_required(view_func):
    """
    Décorateur pour restreindre l'accès aux administrateurs uniquement.
    Les utilisateurs doivent être staff ou superuser pour accéder à la vue.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Vérifier si l'utilisateur est administrateur (staff ou superuser)
        if not (request.user.is_staff or request.user.is_superuser):
            return render(request, 'membres/access_denied.html', {
                'message': 'Accès réservé aux administrateurs',
                'detail': 'Vous n\'avez pas les permissions nécessaires pour accéder à cette page.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def can_modify_members(view_func):
    """
    Décorateur pour vérifier si l'utilisateur peut modifier les membres.
    Seuls les administrateurs peuvent modifier/ajouter des membres et associations.
    """
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        # Vérifier si l'utilisateur a les permissions pour modifier
        if not (request.user.is_staff or request.user.is_superuser):
            return render(request, 'membres/access_denied.html', {
                'message': 'Modification non autorisée',
                'detail': 'Seuls les administrateurs peuvent ajouter ou modifier des membres et associations.'
            }, status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def can_view_member_data(user, membre=None):
    """
    Fonction utilitaire pour vérifier si un utilisateur peut voir les données d'un membre.
    - Les administrateurs peuvent voir tous les membres
    - Les membres ne peuvent voir que leurs propres données
    """
    if user.is_staff or user.is_superuser:
        return True
    
    # Si l'utilisateur est lié à un membre, il peut seulement voir ses propres données
    if hasattr(user, 'membre') and membre:
        return user.membre == membre
    
    return False
