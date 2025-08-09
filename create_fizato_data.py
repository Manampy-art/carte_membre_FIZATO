"""
Script pour créer des données de test pour FIZATO
"""
import os
import sys
import django
from datetime import date

# Configuration Django
sys.path.append('/home/stephanson/Vidéos/carte_membre_FIZATO')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_cartes.settings')
django.setup()

from membres.models import InfoFizato, FonctionBureau, MembreBureau, Membre

def create_fizato_data():
    """Créer les données de base pour FIZATO"""
    
    # 1. Créer les informations FIZATO
    info_fizato, created = InfoFizato.objects.get_or_create(
        nom="FI.ZA.TO",
        defaults={
            'nom_complet': "Fédération Interuniversitaire des Zones Administratives et Techniques de l'Organisation",
            'date_creation': date(2020, 1, 15),
            'devise': "Unis dans la diversité, forts dans l'action",
            'fondateurs': "Dr. Rakoto Maminiaina, Prof. Andry Rasoloson, Ing. Hery Rajaonarison",
            'description': """FI.ZA.TO est une organisation fédératrice qui regroupe plusieurs associations universitaires et techniques. 
Notre mission est de promouvoir l'excellence académique, de faciliter l'échange entre les différentes institutions et de contribuer au développement socio-économique de Madagascar.

Nous œuvrons pour l'unité dans la diversité, en rassemblant des étudiants et professionnels de différents horizons autour d'objectifs communs de développement et d'entraide."""
        }
    )
    
    if created:
        print("✅ Informations FIZATO créées avec succès")
    else:
        print("ℹ️ Informations FIZATO déjà existantes")
    
    # 2. Créer les fonctions du bureau
    fonctions_data = [
        {"nom": "Président", "niveau": 1, "desc": "Dirige l'organisation et représente FIZATO"},
        {"nom": "Vice-président", "niveau": 2, "desc": "Assiste le président et le remplace en cas d'absence"},
        {"nom": "Secrétaire général", "niveau": 3, "desc": "Gère la correspondance et les procès-verbaux"},
        {"nom": "Trésorier", "niveau": 4, "desc": "Responsable des finances et de la comptabilité"},
        {"nom": "Responsable communication", "niveau": 5, "desc": "Gère la communication interne et externe"},
        {"nom": "Responsable technique", "niveau": 6, "desc": "Coordonne les aspects techniques et logistiques"},
    ]
    
    print("\n📋 Création des fonctions du bureau :")
    for fonction_data in fonctions_data:
        fonction, created = FonctionBureau.objects.get_or_create(
            nom=fonction_data["nom"],
            defaults={
                'niveau_hierarchique': fonction_data["niveau"],
                'description': fonction_data["desc"]
            }
        )
        if created:
            print(f"  ✅ {fonction_data['nom']} (niveau {fonction_data['niveau']})")
        else:
            print(f"  ℹ️ {fonction_data['nom']} déjà existant")
    
    print(f"\n🎉 Configuration FIZATO terminée !")
    print(f"📊 Statistiques :")
    print(f"   - Informations FIZATO : {'Créées' if created else 'Déjà présentes'}")
    print(f"   - Fonctions bureau : {FonctionBureau.objects.count()} fonctions")
    print(f"   - Membres bureau : {MembreBureau.objects.filter(est_actuel=True).count()} membres actuels")

if __name__ == "__main__":
    create_fizato_data()
