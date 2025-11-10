#!/usr/bin/env python3
"""
Script de test pour la gestion des budgets avec années fiscales
"""
import sys
import os
sys.path.append('/Users/kader/Desktop/projet-en-cours/budgetmanage')

def test_fiscal_years():
    """Test des années fiscales"""
    try:
        from views.admin_dropdown_options_view import get_valid_dropdown_options
        
        print("🗓️ Test des années fiscales...")
        
        # Récupérer les années fiscales
        annee_fiscale_options = get_valid_dropdown_options('annee_fiscale')
        
        if annee_fiscale_options:
            print(f"✅ {len(annee_fiscale_options)} années fiscales trouvées:")
            for option in annee_fiscale_options:
                print(f"   - {option[1]} (valeur: {option[0]})")
            return True
        else:
            print("❌ Aucune année fiscale trouvée")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test années fiscales: {e}")
        return False

def test_user_budget_model():
    """Test du modèle UserBudget"""
    try:
        from models.user_budget import UserBudgetModel
        
        print("💰 Test du modèle UserBudget...")
        
        # Test création budget
        success = UserBudgetModel.create_budget(1, 2025, 50000.0)
        if success:
            print("✅ Création budget réussie")
        else:
            print("❌ Échec création budget")
            
        # Test récupération budget
        budget = UserBudgetModel.get_user_budget(1, 2025)
        if budget:
            print(f"✅ Budget récupéré: {budget['allocated_budget']}€")
        else:
            print("❌ Budget non trouvé")
            
        # Test résumé
        summary = UserBudgetModel.get_budget_summary_by_year(2025)
        print(f"✅ Résumé 2025: {summary['total_allocated']}€ total")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test UserBudget: {e}")
        return False

def test_users_list():
    """Test de la liste des utilisateurs"""
    try:
        from models.user import UserModel
        
        print("👥 Test des utilisateurs...")
        
        # Test nouvelle méthode
        users = UserModel.get_all_users_list()
        if users:
            print(f"✅ {len(users)} utilisateurs trouvés (liste)")
            for user in users[:3]:  # Afficher les 3 premiers
                print(f"   - {user['prenom']} {user['nom']} ({user['role']})")
        else:
            print("❌ Aucun utilisateur trouvé")
            
        return len(users) > 0
        
    except Exception as e:
        print(f"❌ Erreur test utilisateurs: {e}")
        return False

def main():
    print("🧪 TESTS DE LA GESTION DES BUDGETS")
    print("=" * 40)
    
    # Initialiser la base
    try:
        from models.database import db
        db.init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False
    
    tests = [
        ("Années fiscales", test_fiscal_years),
        ("Modèle UserBudget", test_user_budget_model),
        ("Liste utilisateurs", test_users_list)
    ]
    
    success_count = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Test: {test_name}")
        if test_func():
            success_count += 1
            print(f"✅ {test_name}: RÉUSSI")
        else:
            print(f"❌ {test_name}: ÉCHOUÉ")
    
    print("\n" + "=" * 40)
    print(f"📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("📋 La gestion des budgets est fonctionnelle")
        return True
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        return False

if __name__ == "__main__":
    main()
