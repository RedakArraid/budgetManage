#!/usr/bin/env python3
"""
Script de test rapide pour vérifier les corrections SQL
"""
import sys
import os
sys.path.append('/Users/kader/Desktop/projet-en-cours/budgetmanage')

def test_database_columns():
    """Test que toutes les colonnes nécessaires existent"""
    try:
        from models.database import db
        
        print("🔧 Test des colonnes de la base de données...")
        
        # Vérifier que la colonne fiscal_year existe
        if db.column_exists('demandes', 'fiscal_year'):
            print("✅ Colonne fiscal_year existe")
        else:
            print("❌ Colonne fiscal_year manquante - ajout en cours...")
            db.add_column_if_not_exists('demandes', 'fiscal_year', 'INTEGER')
            print("✅ Colonne fiscal_year ajoutée")
        
        # Tester une requête simple
        result = db.execute_query("SELECT COUNT(*) as count FROM demandes", fetch='one')
        print(f"✅ Requête test réussie: {result['count']} demandes en base")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test database: {e}")
        return False

def test_demande_creation():
    """Test de création d'une demande simple"""
    try:
        from models.demande import DemandeModel
        from models.database import db  # Ajout de l'import manquant
        from controllers.auth_controller import AuthController
        
        print("🔧 Test de création de demande...")
        
        # Simulation d'une création de demande
        success, demande_id = DemandeModel.create_demande(
            user_id=1,  # Admin
            type_demande='budget',
            nom_manifestation='Test Demande',
            client='Client Test',
            date_evenement='2025-07-01',
            lieu='Paris',
            montant=1000.0,
            fy=2025
        )
        
        if success:
            print(f"✅ Demande test créée avec ID: {demande_id}")
            
            # Supprimer la demande test
            db.execute_query("DELETE FROM demandes WHERE id = ?", (demande_id,))
            print("✅ Demande test nettoyée")
            return True
        else:
            print("❌ Échec création demande test")
            return False
            
    except Exception as e:
        print(f"❌ Erreur test création: {e}")
        return False

def test_dashboard_stats():
    """Test des statistiques du tableau de bord"""
    try:
        from models.demande import DemandeModel
        
        print("🔧 Test des statistiques dashboard...")
        
        stats = DemandeModel.get_dashboard_stats(1, 'admin')
        print(f"✅ Statistiques récupérées: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur test stats: {e}")
        return False

def main():
    print("🧪 TESTS DE VÉRIFICATION DES CORRECTIONS SQL")
    print("=" * 50)
    
    # Initialiser la base
    try:
        from models.database import db
        db.init_database()
        print("✅ Base de données initialisée")
    except Exception as e:
        print(f"❌ Erreur initialisation: {e}")
        return False
    
    tests = [
        ("Colonnes de base", test_database_columns),
        ("Création de demande", test_demande_creation), 
        ("Statistiques dashboard", test_dashboard_stats)
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
    
    print("\n" + "=" * 50)
    print(f"📊 RÉSULTATS: {success_count}/{total_tests} tests réussis")
    
    if success_count == total_tests:
        print("🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("📋 Actions recommandées:")
        print("   1. Redémarrez votre application: streamlit run main.py")
        print("   2. Testez la création d'une demande")
        print("   3. Vérifiez le tableau de bord")
        return True
    else:
        print("⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("   Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    main()
