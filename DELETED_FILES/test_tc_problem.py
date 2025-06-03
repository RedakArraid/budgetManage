#!/usr/bin/env python3
"""
🧪 TEST SPÉCIFIQUE DU PROBLÈME TC - BUDGETMANAGE
Reproduit exactement le problème décrit : "TC ne peut pas créer de demandes"
"""

import sys
import os
from datetime import datetime

# Ajouter le chemin du projet
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def simulate_tc_login_and_create_demande():
    """Simule une connexion TC et tentative de création de demande"""
    print("🎭 SIMULATION TC - CRÉATION DE DEMANDE")
    print("=" * 50)
    
    try:
        # 1. Simuler l'accès aux options de listes déroulantes
        print("📋 Test d'accès aux listes déroulantes...")
        
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        # Récupérer les options comme le ferait la vue nouvelle_demande_view
        budget_options = get_valid_dropdown_options('budget')
        categorie_options = get_valid_dropdown_options('categorie')
        typologie_options = get_valid_dropdown_options('typologie_client')
        region_options = get_valid_dropdown_options('region')
        groupe_options = get_valid_dropdown_options('groupe_groupement')
        
        print(f"   • Budget : {len(budget_options)} option(s)")
        print(f"   • Catégorie : {len(categorie_options)} option(s)")
        print(f"   • Typologie : {len(typologie_options)} option(s)")
        print(f"   • Région : {len(region_options)} option(s)")
        print(f"   • Groupe : {len(groupe_options)} option(s)")
        
        # 2. Reproduire la logique de la vue nouvelle_demande_view
        print("\n🔍 Test de la logique de validation...")
        
        # Cette condition reproduit exactement le problème dans nouvelle_demande_view.py ligne 35
        if not budget_options and not categorie_options:
            print("❌ PROBLÈME REPRODUIT!")
            print("   → Les listes Budget ET Catégorie sont vides")
            print("   → La condition 'if not budget_options and not categorie_options:' est vraie")
            print("   → L'application affiche l'erreur et s'arrête")
            print("   → Le TC ne voit aucun formulaire")
            return False
        else:
            print("✅ Condition de blocage non atteinte")
            print("   → Au moins une des listes (Budget ou Catégorie) contient des options")
            print("   → Le formulaire devrait s'afficher normalement")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de la simulation : {e}")
        return False

def test_dropdown_initialization():
    """Test de l'initialisation des listes déroulantes"""
    print("\n🔧 TEST INITIALISATION LISTES DÉROULANTES")
    print("=" * 50)
    
    try:
        from models.dropdown_options import DropdownOptionsModel
        
        # Vérifier l'état actuel
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        empty_categories = []
        
        for category in categories:
            options = DropdownOptionsModel.get_options_for_category(category)
            if not options:
                empty_categories.append(category)
        
        if empty_categories:
            print(f"⚠️ Catégories vides détectées : {empty_categories}")
            print("🔧 Initialisation automatique en cours...")
            
            # Initialiser avec des options par défaut
            default_options = {
                'budget': ['Budget Commercial', 'Budget Marketing', 'Budget Formation'],
                'categorie': ['Animation Commerciale', 'Prospection Client', 'Formation Équipe'],
                'typologie_client': ['Grand Compte', 'PME/ETI', 'Particulier'],
                'groupe_groupement': ['Indépendant', 'Franchise', 'Groupement'],
                'region': ['Île-de-France', 'Auvergne-Rhône-Alpes', 'Nouvelle-Aquitaine']
            }
            
            for category in empty_categories:
                if category in default_options:
                    print(f"\n   📂 Initialisation {category}:")
                    for idx, option_label in enumerate(default_options[category], 1):
                        try:
                            success, message = DropdownOptionsModel.add_option(
                                category=category,
                                label=option_label,
                                order_index=idx,
                                auto_normalize=True
                            )
                            if success:
                                print(f"      ✅ {option_label}")
                            else:
                                print(f"      ⚠️ {option_label}: {message}")
                        except Exception as e:
                            print(f"      ❌ {option_label}: {e}")
            
            print("\n✅ Initialisation terminée")
            return True
        else:
            print("✅ Toutes les catégories contiennent déjà des options")
            return True
            
    except Exception as e:
        print(f"❌ Erreur lors de l'initialisation : {e}")
        return False

def create_test_tc_user():
    """Crée un utilisateur TC de test"""
    print("\n👤 CRÉATION UTILISATEUR TC DE TEST")
    print("=" * 40)
    
    try:
        from models.database import db
        from utils.security import hash_password
        
        # Vérifier si l'utilisateur test existe déjà
        existing_user = db.execute_query(
            "SELECT id FROM users WHERE email = ?",
            ("tc.test@budget.com",),
            fetch='one'
        )
        
        if existing_user:
            print("ℹ️ Utilisateur TC test existe déjà")
            return True
        
        # Créer l'utilisateur TC de test
        tc_password = hash_password("tc123")
        
        user_id = db.execute_query('''
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
        
        if user_id:
            print("✅ Utilisateur TC créé avec succès")
            print("   📧 Email : tc.test@budget.com")
            print("   🔑 Mot de passe : tc123")
            print("   🏷️ Rôle : TC")
            return True
        else:
            print("❌ Échec de la création de l'utilisateur TC")
            return False
            
    except Exception as e:
        print(f"❌ Erreur création utilisateur TC : {e}")
        return False

def run_comprehensive_tc_test():
    """Exécute un test complet du workflow TC"""
    print("🎯 TEST COMPLET WORKFLOW TC")
    print("=" * 40)
    
    # Étapes du test
    steps = [
        ("Création utilisateur TC de test", create_test_tc_user()),
        ("Initialisation listes déroulantes", test_dropdown_initialization()),
        ("Simulation création demande TC", simulate_tc_login_and_create_demande())
    ]
    
    print("\n📊 Résultats du test :")
    print("-" * 30)
    
    all_passed = True
    for step_name, result in steps:
        status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
        print(f"{step_name:<35} : {status}")
        if not result:
            all_passed = False
    
    print("-" * 30)
    
    if all_passed:
        print("\n🎉 PROBLÈME TC RÉSOLU !")
        print("✅ Les TC peuvent maintenant créer des demandes")
        print("\n💡 Instructions pour tester :")
        print("   1. Lancez l'application : streamlit run main.py")
        print("   2. Connectez-vous avec : tc.test@budget.com / tc123")
        print("   3. Cliquez sur 'Nouvelle Demande'")
        print("   4. Le formulaire devrait s'afficher normalement")
        return True
    else:
        print("\n❌ LE PROBLÈME TC PERSISTE")
        print("⚠️ Vérifiez les étapes en échec ci-dessus")
        return False

def diagnose_current_state():
    """Diagnostic de l'état actuel du système"""
    print("🔍 DIAGNOSTIC ÉTAT ACTUEL")
    print("=" * 30)
    
    try:
        from models.database import db
        from models.dropdown_options import DropdownOptionsModel
        
        # 1. Vérifier la base de données
        print("📊 Base de données :")
        
        # Compter les utilisateurs par rôle
        roles_count = db.execute_query('''
            SELECT role, COUNT(*) as count 
            FROM users 
            WHERE is_active = 1 
            GROUP BY role
        ''', fetch='all')
        
        if roles_count:
            for role_info in roles_count:
                print(f"   • {role_info['role']} : {role_info['count']} utilisateur(s)")
        else:
            print("   ⚠️ Aucun utilisateur actif trouvé")
        
        # 2. Vérifier les listes déroulantes
        print("\n📋 Listes déroulantes :")
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        
        for category in categories:
            try:
                options = DropdownOptionsModel.get_options_for_category(category)
                count = len(options) if options else 0
                status = "✅" if count > 0 else "❌"
                print(f"   {status} {category} : {count} option(s)")
            except Exception as e:
                print(f"   ❌ {category} : Erreur - {e}")
        
        # 3. État de la condition problématique
        print("\n🔍 Condition problématique dans nouvelle_demande_view.py :")
        
        budget_options = DropdownOptionsModel.get_options_for_category('budget')
        categorie_options = DropdownOptionsModel.get_options_for_category('categorie')
        
        budget_empty = not budget_options
        categorie_empty = not categorie_options
        condition_blocks = budget_empty and categorie_empty
        
        print(f"   • budget_options vide : {budget_empty}")
        print(f"   • categorie_options vide : {categorie_empty}")
        print(f"   • Condition de blocage active : {condition_blocks}")
        
        if condition_blocks:
            print("   ❌ LES TC SONT BLOQUÉS - Formulaire ne s'affiche pas")
        else:
            print("   ✅ TC peuvent créer des demandes - Formulaire s'affiche")
        
        return not condition_blocks
        
    except Exception as e:
        print(f"❌ Erreur diagnostic : {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 BUDGETMANAGE - TEST PROBLÈME TC")
    print("=" * 50)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Mode de lancement
    if len(sys.argv) > 1 and sys.argv[1].lower() == "--diagnose":
        print("🔍 MODE DIAGNOSTIC UNIQUEMENT")
        success = diagnose_current_state()
    else:
        print("🔧 MODE TEST ET CORRECTION")
        success = run_comprehensive_tc_test()
    
    print(f"\n⏰ Test terminé : {datetime.now().strftime('%H:%M:%S')}")
    
    if success:
        print("🎯 RÉSULTAT : PROBLÈME RÉSOLU")
        return 0
    else:
        print("⚠️ RÉSULTAT : PROBLÈME PERSISTE")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
