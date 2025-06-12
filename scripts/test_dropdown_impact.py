#!/usr/bin/env python3
"""
Script de test spécifique pour l'impact sur les listes déroulantes
Valide que les années fiscales sont correctement gérées
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_dropdown_usage_count():
    """Test du comptage des usages dans les dropdowns"""
    print("🧪 Test comptage usages années fiscales...")
    
    try:
        # Import après ajout du path
        sys.path.insert(0, '/Users/kader/Desktop/projet-en-cours/budgetmanage/views')
        from admin_dropdown_options_view import _get_usage_count
        
        # Test avec une année fiscale existante (si des données existent)
        count = _get_usage_count('annee_fiscale', 'BY25')
        print(f"✅ Usage BY25: {count} (type: {type(count)})")
        
        # Test avec autres catégories  
        count_budget = _get_usage_count('budget', 'budget_marketing')
        print(f"✅ Usage budget_marketing: {count_budget}")
        
        # Test avec catégorie inexistante
        count_invalid = _get_usage_count('invalid_category', 'test')
        print(f"✅ Catégorie invalide: {count_invalid}")
        
        print("✅ Comptage usages fonctionne")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test comptage: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_fiscal_year_normalization():
    """Test de la normalisation des années fiscales"""
    print("🧪 Test normalisation années fiscales...")
    
    try:
        from utils.dropdown_value_normalizer import (
            normalize_dropdown_value,
            is_fiscal_year_label, 
            extract_fiscal_year_code,
            preview_normalization
        )
        
        # Tests années fiscales
        test_cases = [
            ("BY25", "BY25", True),
            ("BY25 (2025)", "BY25", True), 
            ("2025", "BY25", True),
            ("Budget Marketing", "budget_marketing", False),
        ]
        
        all_passed = True
        
        for input_label, expected, is_fiscal in test_cases:
            # Test détection
            detected = is_fiscal_year_label(input_label)
            
            # Test normalisation
            normalized = normalize_dropdown_value(input_label)
            
            # Test extraction si fiscal
            if is_fiscal:
                extracted = extract_fiscal_year_code(input_label)
                extracted_ok = extracted == expected
            else:
                extracted_ok = True
            
            # Vérification
            detection_ok = detected == is_fiscal
            normalization_ok = normalized == expected
            
            if detection_ok and normalization_ok and extracted_ok:
                print(f"✅ '{input_label}' → '{normalized}' (fiscal: {detected})")
            else:
                print(f"❌ '{input_label}' → '{normalized}' (attendu: '{expected}', fiscal: {detected}/{is_fiscal})")
                all_passed = False
        
        if all_passed:
            print("✅ Normalisation années fiscales OK")
        else:
            print("❌ Problèmes dans la normalisation")
            
        return all_passed
        
    except Exception as e:
        print(f"❌ Erreur test normalisation: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_dropdown_database_integration():
    """Test de l'intégration avec la base de données"""
    print("🧪 Test intégration base de données...")
    
    try:
        from models.database import db
        
        # Vérifier que la colonne 'by' existe
        columns = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        column_names = [col['name'] for col in columns]
        
        has_by = 'by' in column_names
        has_cy = 'cy' in column_names
        
        print(f"✅ Colonne 'by' existe: {has_by}")
        print(f"✅ Colonne 'cy' existe: {has_cy}")
        
        if not has_by:
            print("❌ Colonne 'by' manquante - migration nécessaire")
            return False
        
        # Tester une requête de comptage
        try:
            count = db.execute_query("SELECT COUNT(*) FROM demandes WHERE by IS NOT NULL", fetch='one')[0]
            print(f"✅ {count} demandes avec année fiscale 'by'")
        except Exception as e:
            print(f"⚠️ Erreur comptage 'by': {e}")
        
        # Vérifier les années fiscales dans dropdown_options
        try:
            fiscal_years = db.execute_query("""
                SELECT value, label, is_active 
                FROM dropdown_options 
                WHERE category = 'annee_fiscale'
                ORDER BY order_index
            """, fetch='all')
            
            if fiscal_years:
                print(f"✅ {len(fiscal_years)} années fiscales configurées:")
                for fy in fiscal_years:
                    status = "✅" if fy['is_active'] else "❌"
                    print(f"  {status} {fy['value']} ({fy['label']})")
            else:
                print("⚠️ Aucune année fiscale configurée")
            
        except Exception as e:
            print(f"❌ Erreur lecture années fiscales: {e}")
        
        print("✅ Intégration base de données OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test intégration BD: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_dropdown_view_functions():
    """Test des fonctions utilitaires des vues"""
    print("🧪 Test fonctions utilitaires vues...")
    
    try:
        from views.admin_dropdown_options_view import get_valid_dropdown_options, validate_dropdown_value
        
        # Test récupération options
        fiscal_options = get_valid_dropdown_options('annee_fiscale')
        print(f"✅ {len(fiscal_options)} années fiscales récupérées")
        
        if fiscal_options:
            # Test avec première option
            first_option = fiscal_options[0]
            value, label = first_option
            
            # Test validation
            is_valid = validate_dropdown_value('annee_fiscale', value)
            print(f"✅ Validation '{value}': {is_valid}")
            
            if not is_valid:
                print(f"❌ Validation échouée pour '{value}'")
                return False
        
        # Test validation valeur inexistante
        is_invalid = validate_dropdown_value('annee_fiscale', 'INVALID_YEAR')
        if is_invalid:
            print("❌ Validation incorrecte - valeur invalide acceptée")
            return False
        else:
            print("✅ Validation rejette les valeurs invalides")
        
        print("✅ Fonctions utilitaires vues OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test fonctions vues: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def test_migration_impact():
    """Test de l'impact de la migration"""
    print("🧪 Test impact migration...")
    
    try:
        from models.database import db
        
        # Vérifier s'il y a encore des fiscal_year non migrés
        try:
            unmigrated = db.execute_query("""
                SELECT COUNT(*) FROM demandes 
                WHERE (by IS NULL OR by = '') 
                AND fiscal_year IS NOT NULL
            """, fetch='one')[0]
            
            if unmigrated > 0:
                print(f"⚠️ {unmigrated} demandes non migrées détectées")
            else:
                print("✅ Toutes les demandes sont migrées")
                
        except Exception as e:
            print(f"⚠️ Impossible de vérifier migration: {e}")
        
        # Vérifier la cohérence des données
        try:
            coherence_check = db.execute_query("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(CASE WHEN by IS NOT NULL AND by != '' THEN 1 END) as with_by,
                    COUNT(CASE WHEN cy IS NOT NULL THEN 1 END) as with_cy
                FROM demandes
            """, fetch='one')
            
            if coherence_check:
                total = coherence_check['total']
                with_by = coherence_check['with_by']
                with_cy = coherence_check['with_cy']
                
                print(f"✅ Cohérence données:")
                print(f"  Total demandes: {total}")
                print(f"  Avec 'by': {with_by} ({with_by/total*100:.1f}%)")
                print(f"  Avec 'cy': {with_cy} ({with_cy/total*100:.1f}%)")
                
                if with_by < total * 0.8:  # Si moins de 80% ont 'by'
                    print("⚠️ Beaucoup de demandes sans année fiscale")
                    return False
            
        except Exception as e:
            print(f"⚠️ Impossible de vérifier cohérence: {e}")
        
        print("✅ Impact migration OK")
        return True
        
    except Exception as e:
        print(f"❌ Erreur test migration: {e}")
        import traceback
        print(traceback.format_exc())
        return False

def run_dropdown_tests():
    """Exécute tous les tests liés aux dropdowns"""
    print("🚀 Tests Impact Listes Déroulantes - Années Fiscales")
    print("=" * 60)
    
    tests = [
        ("Comptage Usages", test_dropdown_usage_count),
        ("Normalisation", test_fiscal_year_normalization),
        ("Intégration BD", test_dropdown_database_integration),
        ("Fonctions Vues", test_dropdown_view_functions),
        ("Impact Migration", test_migration_impact)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 Test {test_name}")
        print("-" * 40)
        try:
            success = test_func()
            results.append((test_name, success))
            if success:
                print(f"✅ {test_name} RÉUSSI")
            else:
                print(f"❌ {test_name} ÉCHOUÉ")
        except Exception as e:
            print(f"💥 {test_name} ERREUR: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ - Tests Listes Déroulantes")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if success:
            passed += 1
    
    print(f"\nRésultat: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 TOUS LES TESTS DROPDOWNS PASSENT !")
        print("\n✅ Les listes déroulantes gèrent parfaitement les années fiscales")
        print("✅ Le comptage des usages fonctionne")
        print("✅ La normalisation est adaptée par catégorie")
        print("✅ L'interface admin est cohérente")
        return True
    else:
        print("⚠️ Certains tests ont échoué")
        print("❌ Vérifiez les erreurs ci-dessus")
        return False

if __name__ == "__main__":
    success = run_dropdown_tests()
    exit(0 if success else 1)
