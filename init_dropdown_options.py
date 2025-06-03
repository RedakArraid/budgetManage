#!/usr/bin/env python3
"""
Script d'initialisation des listes déroulantes pour BudgetManage
Ajoute les options par défaut nécessaires au fonctionnement de l'application
"""

import sys
import os

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from models.dropdown_options import DropdownOptionsModel

def init_dropdown_options():
    """Initialise les listes déroulantes avec des données par défaut"""
    
    print("🚀 INITIALISATION DES LISTES DÉROULANTES")
    print("=" * 50)
    
    # Vérifier si la base existe et l'initialiser si nécessaire
    try:
        db.init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation DB: {e}")
        return False
    
    # Options par défaut pour chaque catégorie
    default_options = {
        'budget': [
            'Budget Commercial',
            'Budget Marketing', 
            'Budget Formation',
            'Budget Communication',
            'Budget Développement'
        ],
        'categorie': [
            'Animation Commerciale',
            'Prospection Client',
            'Formation Équipe',
            'Événement Marketing',
            'Communication Digitale'
        ],
        'typologie_client': [
            'Grand Compte',
            'PME/ETI',
            'Artisan/Commerçant',
            'Particulier',
            'Collectivité'
        ],
        'groupe_groupement': [
            'Indépendant',
            'Franchise',
            'Groupement Achats',
            'Chaîne Nationale',
            'Coopérative'
        ],
        'region': [
            'Île-de-France',
            'Auvergne-Rhône-Alpes',
            'Nouvelle-Aquitaine',
            'Occitanie',
            'Hauts-de-France',
            'Grand Est',
            'Provence-Alpes-Côte d\'Azur',
            'Pays de la Loire',
            'Bretagne',
            'Normandie',
            'Bourgogne-Franche-Comté',
            'Centre-Val de Loire',
            'Corse'
        ]
    }
    
    total_added = 0
    
    for category, options_list in default_options.items():
        print(f"\n📂 Catégorie: {category}")
        print("-" * 30)
        
        category_count = 0
        
        for idx, option_label in enumerate(options_list, 1):
            try:
                success, message = DropdownOptionsModel.add_option(
                    category=category,
                    label=option_label,
                    order_index=idx,
                    auto_normalize=True
                )
                
                if success:
                    print(f"  ✅ {option_label}")
                    category_count += 1
                    total_added += 1
                else:
                    print(f"  ⚠️ {option_label}: {message}")
                    
            except Exception as e:
                print(f"  ❌ {option_label}: {e}")
        
        print(f"📊 {category_count}/{len(options_list)} options ajoutées")
    
    print(f"\n🎉 RÉSUMÉ:")
    print(f"✅ {total_added} options au total ajoutées")
    print(f"📂 {len(default_options)} catégories initialisées")
    
    return total_added > 0

def check_existing_options():
    """Vérifie les options existantes"""
    print("\n🔍 VÉRIFICATION DES OPTIONS EXISTANTES")
    print("=" * 50)
    
    categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
    
    for category in categories:
        try:
            options = DropdownOptionsModel.get_options_for_category(category)
            print(f"📂 {category}: {len(options)} option(s)")
            
            for opt in options[:3]:  # Afficher les 3 premières
                print(f"  - {opt['label']} (valeur: {opt['value']})")
            
            if len(options) > 3:
                print(f"  ... et {len(options) - 3} autre(s)")
                
        except Exception as e:
            print(f"❌ Erreur pour {category}: {e}")

def main():
    """Fonction principale"""
    print("🔧 BUDGETMANAGE - INITIALISATION LISTES DÉROULANTES")
    print("=" * 60)
    
    # Vérifier d'abord l'état actuel
    check_existing_options()
    
    # Demander confirmation
    print("\n❓ Voulez-vous initialiser les listes déroulantes avec les données par défaut ?")
    response = input("Tapez 'OUI' pour continuer: ")
    
    if response.upper() == 'OUI':
        success = init_dropdown_options()
        
        if success:
            print("\n✅ Initialisation terminée avec succès !")
            print("\n💡 Les TC peuvent maintenant créer des demandes")
            print("🎯 Connectez-vous en tant qu'admin pour personnaliser les options")
            
            # Vérification finale
            check_existing_options()
        else:
            print("\n❌ Échec de l'initialisation")
    else:
        print("❌ Initialisation annulée")

if __name__ == "__main__":
    main()
