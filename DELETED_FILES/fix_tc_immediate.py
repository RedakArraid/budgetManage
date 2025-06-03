#!/usr/bin/env python3
"""
🔧 CORRECTION IMMÉDIATE DU PROBLÈME TC - BUDGETMANAGE
Script de correction rapide pour résoudre immédiatement le problème
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def apply_immediate_fix():
    """Applique la correction immédiate pour débloquer les TC"""
    print("🚀 CORRECTION IMMÉDIATE DU PROBLÈME TC")
    print("=" * 50)
    
    try:
        # 1. Initialiser la base de données
        print("📊 Initialisation de la base de données...")
        from models.database import db
        db.init_database()
        print("✅ Base de données initialisée")
        
        # 2. Créer admin par défaut si nécessaire
        print("\n👤 Vérification administrateur...")
        admin_count = db.execute_query(
            "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = 1",
            fetch='one'
        )[0]
        
        if admin_count == 0:
            from utils.security import hash_password
            admin_password = hash_password("admin123")
            
            db.execute_query('''
                INSERT OR REPLACE INTO users 
                (id, email, password_hash, nom, prenom, role, is_active, activated_at)
                VALUES (1, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                "admin@budget.com", 
                admin_password, 
                "Administrateur", 
                "Système", 
                "admin", 
                True
            ))
            print("✅ Administrateur créé : admin@budget.com / admin123")
        else:
            print(f"✅ {admin_count} administrateur(s) existant(s)")
        
        # 3. Initialiser les listes déroulantes
        print("\n📋 Initialisation des listes déroulantes...")
        from models.dropdown_options import DropdownOptionsModel
        
        # Options essentielles pour débloquer les TC
        essential_options = {
            'budget': [
                'Budget Commercial',
                'Budget Marketing', 
                'Budget Formation',
                'Budget Communication'
            ],
            'categorie': [
                'Animation Commerciale',
                'Prospection Client',
                'Formation Équipe',
                'Événement Marketing'
            ],
            'typologie_client': [
                'Grand Compte',
                'PME/ETI',
                'Artisan/Commerçant',
                'Particulier'
            ],
            'groupe_groupement': [
                'Indépendant',
                'Franchise',
                'Groupement Achats',
                'Chaîne Nationale'
            ],
            'region': [
                'Île-de-France',
                'Auvergne-Rhône-Alpes',
                'Nouvelle-Aquitaine',
                'Occitanie',
                'Hauts-de-France'
            ]
        }
        
        total_added = 0
        for category, options_list in essential_options.items():
            print(f"\n   📂 {category}:")
            for idx, option_label in enumerate(options_list, 1):
                try:
                    success, message = DropdownOptionsModel.add_option(
                        category=category,
                        label=option_label,
                        order_index=idx,
                        auto_normalize=True
                    )
                    
                    if success:
                        print(f"      ✅ {option_label}")
                        total_added += 1
                    else:
                        if "déjà existe" in message.lower():
                            print(f"      ℹ️ {option_label} (existant)")
                        else:
                            print(f"      ⚠️ {option_label}: {message}")
                        
                except Exception as e:
                    print(f"      ❌ {option_label}: {e}")
        
        print(f"\n✅ {total_added} nouvelles options ajoutées")
        
        # 4. Créer un utilisateur TC de test
        print("\n👤 Création utilisateur TC de test...")
        
        # Vérifier si l'utilisateur test existe déjà
        existing_tc = db.execute_query(
            "SELECT id FROM users WHERE email = ?",
            ("tc.test@budget.com",),
            fetch='one'
        )
        
        if not existing_tc:
            from utils.security import hash_password
            tc_password = hash_password("tc123")
            
            tc_id = db.execute_query('''
                INSERT INTO users (email, password_hash, nom, prenom, role, region, is_active, activated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                "tc.test@budget.com",
                tc_password,
                "Test",
                "TC",
                "tc",
                "Île-de-France",
                True
            ), fetch='lastrowid')
            
            if tc_id:
                print("✅ TC test créé : tc.test@budget.com / tc123")
            else:
                print("❌ Échec création TC test")
        else:
            print("ℹ️ TC test existe déjà")
        
        # 5. Vérification finale
        print("\n🔍 Vérification finale...")
        
        # Test de la condition problématique
        budget_options = DropdownOptionsModel.get_options_for_category('budget')
        categorie_options = DropdownOptionsModel.get_options_for_category('categorie')
        
        if budget_options and categorie_options:
            print("✅ Condition de blocage résolue !")
            print(f"   • Budget : {len(budget_options)} option(s)")
            print(f"   • Catégorie : {len(categorie_options)} option(s)")
            return True
        else:
            print("❌ Problème persiste")
            print(f"   • Budget : {len(budget_options) if budget_options else 0} option(s)")
            print(f"   • Catégorie : {len(categorie_options) if categorie_options else 0} option(s)")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction : {e}")
        return False

def verify_tc_can_create_demande():
    """Vérifie que les TC peuvent maintenant créer des demandes"""
    print("\n🧪 VÉRIFICATION FINALE")
    print("=" * 30)
    
    try:
        # Simuler l'accès à la vue nouvelle_demande_view
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        budget_options = get_valid_dropdown_options('budget')
        categorie_options = get_valid_dropdown_options('categorie')
        
        # Reproduire la condition problématique
        condition_blocks = not budget_options and not categorie_options
        
        print(f"🔍 Test condition de blocage:")
        print(f"   • budget_options vide : {not budget_options}")
        print(f"   • categorie_options vide : {not categorie_options}")
        print(f"   • Condition bloquante active : {condition_blocks}")
        
        if condition_blocks:
            print("\n❌ PROBLÈME PERSISTE")
            print("   → Les TC restent bloqués")
            return False
        else:
            print("\n✅ PROBLÈME RÉSOLU")
            print("   → Les TC peuvent créer des demandes")
            return True
            
    except Exception as e:
        print(f"❌ Erreur vérification : {e}")
        return False

def display_success_instructions():
    """Affiche les instructions de succès"""
    print("\n🎉 CORRECTION RÉUSSIE !")
    print("=" * 30)
    
    print("\n🚀 PROCHAINES ÉTAPES :")
    print("1. Lancez l'application :")
    print("   streamlit run main.py")
    print()
    print("2. Testez avec le compte admin :")
    print("   📧 Email : admin@budget.com")
    print("   🔑 Mot de passe : admin123")
    print()
    print("3. Testez avec le compte TC :")
    print("   📧 Email : tc.test@budget.com")
    print("   🔑 Mot de passe : tc123")
    print()
    print("4. Cliquez sur '➕ Nouvelle Demande'")
    print("   ✅ Le formulaire devrait s'afficher normalement")
    print()
    print("⚠️ IMPORTANT : Changez les mots de passe par défaut en production !")

def main():
    """Fonction principale"""
    print("🔧 BUDGETMANAGE - CORRECTION IMMÉDIATE TC")
    print("=" * 60)
    print(f"⏰ Début : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Appliquer la correction
    success = apply_immediate_fix()
    
    if success:
        # Vérifier que ça fonctionne
        verification_success = verify_tc_can_create_demande()
        
        if verification_success:
            display_success_instructions()
            print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
            print("\n🎯 RÉSULTAT : SUCCÈS COMPLET")
            return 0
        else:
            print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
            print("\n⚠️ RÉSULTAT : CORRECTION PARTIELLE")
            print("💡 La correction a été appliquée mais la vérification a échoué")
            print("🔧 Essayez de relancer le script ou contactez le support")
            return 1
    else:
        print(f"\n⏰ Fin : {datetime.now().strftime('%H:%M:%S')}")
        print("\n❌ RÉSULTAT : ÉCHEC DE LA CORRECTION")
        print("💡 Vérifiez les erreurs ci-dessus")
        print("🔧 Essayez le script complet : python validate_and_fix.py")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
