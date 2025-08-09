from django.urls import path
from . import views

urlpatterns = [
    # Authentification
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('mes-informations/', views.modifier_mes_informations, name='modifier_mes_informations'),
    
    path('', views.dashboard, name='dashboard'),
    
    # Associations
    path('associations/', views.liste_associations, name='liste_associations'),
    path('associations/ajouter/', views.ajouter_association, name='ajouter_association'),
    path('associations/<int:association_id>/', views.detail_association, name='detail_association'),
    path('associations/<int:association_id>/modifier/', views.modifier_association, name='modifier_association'),
    path('associations/<int:association_id>/supprimer/', views.supprimer_association, name='supprimer_association'),
    
    # Membres
    path('membres/', views.liste_membres, name='liste_membres'),
    path('membres/ajouter/', views.ajouter_membre, name='ajouter_membre'),
    path('membres/ajouter/<int:association_id>/', views.ajouter_membre, name='ajouter_membre_association'),
    path('membres/<int:membre_id>/modifier/', views.modifier_membre, name='modifier_membre'),
    path('membres/<int:membre_id>/supprimer/', views.supprimer_membre, name='supprimer_membre'),
    
    # Cartes
    path('cartes/', views.liste_cartes_membres, name='liste_cartes_membres'),
    path('cartes/generer/', views.generer_cartes, name='generer_cartes'),
    path('cartes/imprimer/<int:membre_id>/', views.print_carte_membre, name='print_carte_membre'),
    path('cartes/imprimer-multiples/<str:membres_ids>/', views.print_cartes_multiples, name='print_cartes_multiples'),
    
    # FIZATO Management
    path('fizato/', views.detail_fizato, name='detail_fizato'),
    path('fizato/historique/', views.historique_fizato, name='historique_fizato'),
    path('fizato/historique/vider/', views.vider_historique, name='vider_historique'),
    path('fizato/historique/supprimer/<int:mandat_id>/', views.supprimer_mandat_archive, name='supprimer_mandat_archive'),
    path('fizato/info/ajouter/', views.ajouter_info_fizato, name='ajouter_info_fizato'),
    path('fizato/fonction/ajouter/', views.ajouter_fonction_bureau, name='ajouter_fonction_bureau'),
    path('fizato/fonction/<int:fonction_id>/modifier/', views.modifier_fonction_bureau, name='modifier_fonction_bureau'),
    path('fizato/fonction/<int:fonction_id>/supprimer/', views.supprimer_fonction_bureau, name='supprimer_fonction_bureau'),
    path('fizato/bureau/ajouter/', views.ajouter_membre_bureau, name='ajouter_membre_bureau'),
    path('fizato/bureau/<int:membre_bureau_id>/supprimer/', views.supprimer_membre_bureau, name='supprimer_membre_bureau'),
    path('fizato/bureau/<int:membre_bureau_id>/detail/', views.detail_membre_bureau, name='detail_membre_bureau'),
    path('fizato/mandat/terminer/', views.terminer_mandat, name='terminer_mandat'),
    path('fizato/mandat/bureau/terminer/', views.terminer_mandat_bureau, name='terminer_mandat_bureau'),
    path('fizato/mandat/creer/', views.creer_mandat, name='creer_mandat'),
    path('fizato/doyen/ajouter/', views.ajouter_comite_doyen, name='ajouter_comite_doyen'),
    path('fizato/doyen/<int:doyen_id>/supprimer/', views.supprimer_comite_doyen, name='supprimer_comite_doyen'),
]