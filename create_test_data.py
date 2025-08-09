#!/usr/bin/env python
"""
Script pour créer des données de test pour l'application FIZATO
"""
import os
import sys
import django
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_cartes.settings')
django.setup()

from membres.models import Association, Membre, CarteMembre

def create_test_data():
    """Créer des données de test"""
    
    # Créer des associations
    association1, created = Association.objects.get_or_create(
        nom="Association des Étudiants en Informatique",
        defaults={}
    )
    
    association2, created = Association.objects.get_or_create(
        nom="Club de Robotique FIZATO",
        defaults={}
    )
    
    association3, created = Association.objects.get_or_create(
        nom="Association des Futurs Ingénieurs",
        defaults={}
    )
    
    # Créer des membres
    membres_data = [
        {
            'nom': 'Benali',
            'prenom': 'Ahmed',
            'numero_cin': 'AB123456',
            'association': association1,
            'filiere': 'Informatique',
            'parcours': 'Génie Logiciel',
            'numero_carte': 'CARD001'
        },
        {
            'nom': 'Trabelsi',
            'prenom': 'Fatima',
            'numero_cin': 'CD789012',
            'association': association1,
            'filiere': 'Informatique',
            'parcours': 'Réseaux et Sécurité',
            'numero_carte': 'CARD002'
        },
        {
            'nom': 'Khemir',
            'prenom': 'Mohamed',
            'numero_cin': 'EF345678',
            'association': association2,
            'filiere': 'Électronique',
            'parcours': 'Robotique',
            'numero_carte': 'CARD003'
        },
        {
            'nom': 'Sassi',
            'prenom': 'Amira',
            'numero_cin': 'GH901234',
            'association': association2,
            'filiere': 'Mécanique',
            'parcours': 'Mécatronique',
            'numero_carte': 'CARD004'
        },
        {
            'nom': 'Hajji',
            'prenom': 'Youssef',
            'numero_cin': 'IJ567890',
            'association': association3,
            'filiere': 'Génie Civil',
            'parcours': 'Construction',
            'numero_carte': 'CARD005'
        }
    ]
    
    # Dates de validité
    date_debut = date.today()
    date_fin = date_debut + timedelta(days=365)  # Valide 1 an
    
    membres_crees = []
    for membre_data in membres_data:
        membre, created = Membre.objects.get_or_create(
            numero_cin=membre_data['numero_cin'],
            defaults={
                **membre_data,
                'date_debut': date_debut,
                'date_fin': date_fin
            }
        )
        if created:
            membres_crees.append(membre)
            print(f"✓ Membre créé: {membre.prenom} {membre.nom}")
        else:
            print(f"• Membre existe déjà: {membre.prenom} {membre.nom}")
    
    # Créer des cartes pour quelques membres
    cartes_creees = 0
    for membre in membres_crees[:3]:  # Créer des cartes pour les 3 premiers
        carte, created = CarteMembre.objects.get_or_create(membre=membre)
        if created:
            cartes_creees += 1
            print(f"✓ Carte créée pour: {membre.prenom} {membre.nom}")
    
    print(f"\n🎉 Données de test créées avec succès!")
    print(f"   - {Association.objects.count()} associations")
    print(f"   - {Membre.objects.count()} membres")
    print(f"   - {CarteMembre.objects.count()} cartes générées")

if __name__ == '__main__':
    create_test_data()
