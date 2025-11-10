#!/usr/bin/env python3
"""
Test des corrections appliquées au système d'années fiscales
Valide que les corrections améliorent la cohérence sans introduire de régressions
"""
import sys
import os
from datetime import datetime

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.fiscal_year_utils import (
    byxx_to_year, year_to_byxx, get_fiscal_year_from_date,
    validate_fiscal_year_format, validate_byxx_format, get_current_fiscal_year
)

def test_corrections():
    """Test toutes les corrections appliquées"""
    print("🧪 TEST DES CORRECTIONS APPLIQUÉES")
    print("=" * 50)
    
    results = {
        'basic_conversions': test_basic_conversions(),
        'validation_functions': test_validation_functions(),
        'edge_cases': test_edge_cases(),
        'current_fiscal_year': test_current_fiscal_year(),
        'error_handling': test_error_handling()
    }
    
    # Résumé
    print("\n" + "=" * 50)
    print("📊 RÉSUMÉ DES TESTS")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 RÉSULTAT: {'✅ TOUTES LES CORRECTIONS VALIDÉES' if all_passed else '❌ PROBLÈMES DÉTECTÉS'}")
    return all_passed

def test_basic_conversions():
    """Test des conversions de base"""
    print("\n1️⃣ TEST CONVERSIONS DE BASE")
    
    test_cases = [
        ('BY25', 2024, 'BY25 → 2024'),
        ('BY24', 2023, 'BY24 → 2023'),
        ('BY26', 2025, 'BY26 → 2025'),
        ('BY20', 2019, 'BY20 → 2019'),
        ('BY30', 2029, 'BY30 → 2029'),
    ]
    
    all_passed = True
    
    for byxx, expected_year, desc in test_cases:
        # Test BYXX → année
        result_year = byxx_to_year(byxx)
        year_ok = result_year == expected_year
        
        # Test année → BYXX
        result_byxx = year_to_byxx(expected_year)
        byxx_ok = result_byxx == byxx
        
        # Test bidirectionnalité
        bidirectional_ok = year_ok and byxx_ok
        
        status = "✅" if bidirectional_ok else "❌"
        print(f"   {status} {desc}: {result_year} ↔ {result_byxx}")
        
        if not bidirectional_ok:
            all_passed = False
            if not year_ok:
                print(f"      ❌ Conversion BYXX: {byxx} → {result_year} (attendu: {expected_year})")
            if not byxx_ok:
                print(f"      ❌ Conversion année: {expected_year} → {result_byxx} (attendu: {byxx})")
    
    return all_passed

def test_validation_functions():
    """Test des nouvelles fonctions de validation"""
    print("\n2️⃣ TEST FONCTIONS DE VALIDATION")
    
    # Test validate_byxx_format
    validation_tests = [
        ('BY25', True, 'Format valide'),
        ('BY99', True, 'Limite haute'),
        ('BY00', True, 'Limite basse'),
        ('B25', False, 'Manque Y'),
        ('BY2', False, 'Trop court'),
        ('BY255', False, 'Trop long'),
        ('BYAA', False, 'Non numérique'),
        ('', False, 'Vide'),
        (None, False, 'None'),
        (25, False, 'Non string'),
    ]
    
    all_passed = True
    
    print("   🔍 Test validate_byxx_format():")
    for value, expected_valid, desc in validation_tests:
        try:
            is_valid, error_msg = validate_byxx_format(value)
            test_ok = is_valid == expected_valid
            status = "✅" if test_ok else "❌"
            print(f"      {status} {desc}: '{value}' → {is_valid}")
            if not test_ok:
                print(f"         Attendu: {expected_valid}, Obtenu: {is_valid}")
                all_passed = False
        except Exception as e:
            print(f"      ❌ Erreur test '{value}': {e}")
            all_passed = False
    
    # Test validate_fiscal_year_format
    print("   🔍 Test validate_fiscal_year_format():")
    fiscal_tests = [
        ('BY25', True, 2024, 'Format valide complet'),
        ('BY51', False, 1950, 'Année hors plage métier (1950 < 2000)'),
        ('invalid', False, None, 'Format invalide'),
    ]
    
    for value, expected_valid, expected_year, desc in fiscal_tests:
        try:
            is_valid, converted_year, error_msg = validate_fiscal_year_format(value)
            test_ok = (is_valid == expected_valid) and (converted_year == expected_year)
            status = "✅" if test_ok else "❌"
            print(f"      {status} {desc}: '{value}' → {is_valid}, {converted_year}")
            if not test_ok:
                all_passed = False
        except Exception as e:
            print(f"      ❌ Erreur test '{value}': {e}")
            all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test des cas limites"""
    print("\n3️⃣ TEST CAS LIMITES")
    
    edge_cases = [
        ('2024-04-30', 'BY24', 'Fin période fiscale'),
        ('2024-05-01', 'BY25', 'Début période fiscale'),
        ('2024-12-31', 'BY25', 'Fin année civile'),
        ('2025-01-01', 'BY25', 'Début année civile'),
        ('2025-04-30', 'BY25', 'Fin période suivante'),
        ('2025-05-01', 'BY26', 'Début période suivante'),
    ]
    
    all_passed = True
    
    for date_str, expected_byxx, desc in edge_cases:
        try:
            result = get_fiscal_year_from_date(date_str)
            test_ok = result == expected_byxx
            status = "✅" if test_ok else "❌"
            print(f"   {status} {desc}: {date_str} → {result} (attendu: {expected_byxx})")
            if not test_ok:
                all_passed = False
        except Exception as e:
            print(f"   ❌ Erreur test '{date_str}': {e}")
            all_passed = False
    
    return all_passed

def test_current_fiscal_year():
    """Test de la fonction get_current_fiscal_year"""
    print("\n4️⃣ TEST ANNÉE FISCALE ACTUELLE")
    
    try:
        current_fy = get_current_fiscal_year()
        
        if current_fy:
            # Vérifier le format
            is_valid, error_msg = validate_byxx_format(current_fy)
            if is_valid:
                print(f"   ✅ Année fiscale actuelle: {current_fy}")
                
                # Vérifier la cohérence avec la date d'aujourd'hui
                from datetime import date
                today_fy = get_fiscal_year_from_date(date.today().strftime('%Y-%m-%d'))
                
                if current_fy == today_fy:
                    print(f"   ✅ Cohérence avec date du jour: {today_fy}")
                    return True
                else:
                    print(f"   ❌ Incohérence: get_current_fiscal_year()={current_fy}, date_du_jour={today_fy}")
                    return False
            else:
                print(f"   ❌ Format invalide: {current_fy} ({error_msg})")
                return False
        else:
            print("   ❌ get_current_fiscal_year() retourne None")
            return False
            
    except Exception as e:
        print(f"   ❌ Erreur test année actuelle: {e}")
        return False

def test_error_handling():
    """Test de la gestion d'erreurs"""
    print("\n5️⃣ TEST GESTION D'ERREURS")
    
    error_cases = [
        (None, 'None value'),
        ('', 'Empty string'),
        ('invalid', 'Invalid format'),
        (123, 'Non-string type'),
        ('BY', 'Incomplete format'),
        ('BY999', 'Out of range'),
    ]
    
    all_passed = True
    
    for invalid_value, desc in error_cases:
        try:
            # Test byxx_to_year ne lève pas d'exception
            result = byxx_to_year(invalid_value)
            if result is None:
                print(f"   ✅ {desc}: byxx_to_year() retourne None (correct)")
            else:
                print(f"   ❌ {desc}: byxx_to_year() devrait retourner None, obtenu: {result}")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ {desc}: byxx_to_year() lève une exception: {e}")
            all_passed = False
        
        try:
            # Test validate_byxx_format gère les erreurs proprement
            is_valid, error_msg = validate_byxx_format(invalid_value)
            if not is_valid and error_msg:
                print(f"   ✅ {desc}: validate_byxx_format() gère l'erreur: {error_msg}")
            else:
                print(f"   ❌ {desc}: validate_byxx_format() devrait être False avec message")
                all_passed = False
                
        except Exception as e:
            print(f"   ❌ {desc}: validate_byxx_format() lève une exception: {e}")
            all_passed = False
    
    return all_passed

def run_integration_test():
    """Test d'intégration simulant l'utilisation réelle"""
    print("\n🔗 TEST D'INTÉGRATION")
    
    # Simuler le workflow complet d'une nouvelle demande
    try:
        # 1. Utilisateur sélectionne BY25 dans l'interface
        user_selection = "BY25"
        print(f"   1. Sélection utilisateur: {user_selection}")
        
        # 2. Validation de l'entrée
        is_valid, fiscal_year, error_msg = validate_fiscal_year_format(user_selection)
        if not is_valid:
            print(f"   ❌ Validation échouée: {error_msg}")
            return False
        print(f"   2. Validation OK: {user_selection} → année {fiscal_year}")
        
        # 3. Conversion pour stockage en base
        by_for_db = user_selection  # Format BYXX stocké tel quel
        fy_for_db = fiscal_year     # Année de début pour requêtes
        print(f"   3. Stockage DB: by='{by_for_db}', fiscal_year={fy_for_db}")
        
        # 4. Reconversion pour affichage
        display_by = year_to_byxx(fy_for_db)
        if display_by != user_selection:
            print(f"   ❌ Perte de cohérence: {user_selection} → {fy_for_db} → {display_by}")
            return False
        print(f"   4. Reconversion OK: {fy_for_db} → {display_by}")
        
        # 5. Test avec date d'événement
        event_date = "2024-06-15"  # Juin 2024
        expected_fy_from_date = get_fiscal_year_from_date(event_date)
        if expected_fy_from_date != user_selection:
            print(f"   ⚠️ Incohérence date: {event_date} → {expected_fy_from_date} (utilisateur: {user_selection})")
            # Ce n'est pas forcément une erreur si l'utilisateur choisit une année différente
        
        print(f"   ✅ Workflow complet validé: {user_selection} ↔ {fiscal_year}")
        return True
        
    except Exception as e:
        print(f"   ❌ Erreur workflow: {e}")
        return False

if __name__ == "__main__":
    print("🚀 VALIDATION DES CORRECTIONS SYSTÈME ANNÉES FISCALES")
    print(f"📅 Date d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n🎯 Objectif: Valider que les corrections améliorent la cohérence")
    
    try:
        # Tests principaux
        success = test_corrections()
        
        # Test d'intégration
        integration_success = run_integration_test()
        
        # Résultat final
        if success and integration_success:
            print("\n🎉 TOUTES LES CORRECTIONS SONT VALIDÉES!")
            print("✅ Le système d'années fiscales est maintenant parfaitement cohérent")
            print("💡 Les corrections appliquées améliorent la robustesse sans régression")
            exit_code = 0
        else:
            print("\n❌ PROBLÈMES DÉTECTÉS DANS LES CORRECTIONS")
            print("⚠️ Vérifiez les erreurs ci-dessus et corrigez si nécessaire")
            exit_code = 1
        
        sys.exit(exit_code)
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
