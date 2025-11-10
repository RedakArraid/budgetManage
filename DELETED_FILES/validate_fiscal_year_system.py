#!/usr/bin/env python3
"""
Script de validation complète du système d'années fiscales
Vérifie la cohérence entre tous les composants du projet BudgetManage
"""
import sys
import os
from datetime import datetime, date

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from utils.fiscal_year_utils import byxx_to_year, year_to_byxx, get_fiscal_year_from_date

def main():
    """Validation complète du système d'années fiscales"""
    print("🔍 VALIDATION COMPLÈTE - SYSTÈME ANNÉES FISCALES")
    print("=" * 60)
    
    results = {
        'conversions': test_conversions(),
        'database_structure': test_database_structure(),
        'database_data': test_database_data(),
        'dropdown_options': test_dropdown_options(),
        'edge_cases': test_edge_cases(),
        'consistency': test_consistency()
    }
    
    # Affichage du résumé
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DE LA VALIDATION")
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print(f"\n🎯 RÉSULTAT GLOBAL: {'✅ TOUS LES TESTS PASSÉS' if all_passed else '❌ ÉCHECS DÉTECTÉS'}")
    
    if all_passed:
        print("💡 Le système d'années fiscales est cohérent et prêt pour la production.")
    else:
        print("⚠️ Des corrections sont nécessaires avant la mise en production.")
    
    return all_passed

def test_conversions():
    """Test des fonctions de conversion BYXX ↔ année"""
    print("\n1️⃣ TEST DES CONVERSIONS")
    
    test_cases = [
        # (byxx, expected_year, description)
        ('BY24', 2023, 'BY24 → 2023'),
        ('BY25', 2024, 'BY25 → 2024'), 
        ('BY26', 2025, 'BY26 → 2025'),
        ('BY20', 2019, 'BY20 → 2019'),
        ('BY30', 2029, 'BY30 → 2029'),
    ]
    
    all_passed = True
    
    print("   🔄 Tests BYXX → année:")
    for byxx, expected_year, desc in test_cases:
        result = byxx_to_year(byxx)
        passed = result == expected_year
        status = "✅" if passed else "❌"
        print(f"      {status} {desc}: {result}")
        if not passed:
            all_passed = False
    
    print("   🔄 Tests année → BYXX:")
    for byxx, year, desc in test_cases:
        result = year_to_byxx(year)
        passed = result == byxx
        status = "✅" if passed else "❌"
        print(f"      {status} {year} → {result} (attendu: {byxx})")
        if not passed:
            all_passed = False
    
    # Test bidirectionnalité
    print("   🔄 Tests bidirectionnalité:")
    for byxx, year, _ in test_cases:
        converted_year = byxx_to_year(byxx)
        back_to_byxx = year_to_byxx(converted_year) if converted_year else None
        passed = back_to_byxx == byxx
        status = "✅" if passed else "❌"
        print(f"      {status} {byxx} → {converted_year} → {back_to_byxx}")
        if not passed:
            all_passed = False
    
    return all_passed

def test_database_structure():
    """Test de la structure de la base de données"""
    print("\n2️⃣ TEST STRUCTURE BASE DE DONNÉES")
    
    all_passed = True
    
    try:
        # Test table demandes
        print("   📋 Table demandes:")
        columns = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        column_names = [col['name'] for col in columns]
        
        required_columns = ['cy', 'by', 'fiscal_year']
        for col in required_columns:
            if col in column_names:
                print(f"      ✅ Colonne {col} présente")
            else:
                print(f"      ❌ Colonne {col} manquante")
                all_passed = False
        
        # Test table dropdown_options
        print("   📋 Table dropdown_options:")
        dropdown_exists = db.table_exists('dropdown_options')
        if dropdown_exists:
            print("      ✅ Table dropdown_options présente")
            
            # Vérifier données années fiscales
            fiscal_options = db.execute_query(
                "SELECT COUNT(*) FROM dropdown_options WHERE category = 'annee_fiscale'",
                fetch='one'
            )[0]
            print(f"      📊 {fiscal_options} années fiscales configurées")
        else:
            print("      ❌ Table dropdown_options manquante")
            all_passed = False
            
    except Exception as e:
        print(f"      ❌ Erreur structure DB: {e}")
        all_passed = False
    
    return all_passed

def test_database_data():
    """Test de la cohérence des données en base"""
    print("\n3️⃣ TEST DONNÉES BASE")
    
    all_passed = True
    
    try:
        # Récupérer toutes les demandes avec années fiscales
        demandes = db.execute_query("""
            SELECT id, cy, by, fiscal_year, date_evenement
            FROM demandes 
            WHERE date_evenement IS NOT NULL
            LIMIT 10
        """, fetch='all')
        
        if not demandes:
            print("   📊 Aucune demande avec date en base")
            return True
        
        print(f"   📊 Vérification de {len(demandes)} demandes:")
        
        for demande in demandes:
            demande_id = demande['id']
            cy = demande['cy']
            by = demande['by']
            fiscal_year = demande['fiscal_year']
            date_evenement = demande['date_evenement']
            
            # Test cohérence cy avec date_evenement
            if date_evenement:
                try:
                    expected_cy = datetime.strptime(date_evenement, '%Y-%m-%d').year
                    cy_ok = cy == expected_cy
                    
                    # Test cohérence by avec fiscal_year
                    if fiscal_year:
                        expected_by = year_to_byxx(fiscal_year)
                        by_ok = by == expected_by
                    else:
                        by_ok = True  # Pas de fiscal_year défini
                    
                    if cy_ok and by_ok:
                        print(f"      ✅ Demande #{demande_id}: cy={cy}, by={by}, fy={fiscal_year}")
                    else:
                        print(f"      ❌ Demande #{demande_id}: incohérence détectée")
                        if not cy_ok:
                            print(f"         • cy={cy} != {expected_cy} (date: {date_evenement})")
                        if not by_ok:
                            print(f"         • by={by} != {expected_by} (fy: {fiscal_year})")
                        all_passed = False
                        
                except Exception as e:
                    print(f"      ⚠️ Demande #{demande_id}: erreur validation ({e})")
            
    except Exception as e:
        print(f"   ❌ Erreur test données: {e}")
        all_passed = False
    
    return all_passed

def test_dropdown_options():
    """Test des options dropdown années fiscales"""
    print("\n4️⃣ TEST DROPDOWN OPTIONS")
    
    all_passed = True
    
    try:
        # Récupérer les années fiscales
        fiscal_options = db.execute_query("""
            SELECT value, label, is_active, order_index
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not fiscal_options:
            print("   ⚠️ Aucune année fiscale configurée dans dropdown_options")
            return False
        
        print(f"   📊 {len(fiscal_options)} années fiscales configurées:")
        
        for option in fiscal_options:
            value = option['value']
            label = option['label']
            is_active = option['is_active']
            
            # Vérifier format BYXX
            if value.startswith('BY') and len(value) == 4:
                try:
                    year = byxx_to_year(value)
                    if year:
                        status = "✅ Actif" if is_active else "⚪ Inactif"
                        print(f"      {status} {value}: {label} (année: {year})")
                    else:
                        print(f"      ❌ {value}: conversion impossible")
                        all_passed = False
                except Exception as e:
                    print(f"      ❌ {value}: erreur conversion ({e})")
                    all_passed = False
            else:
                print(f"      ❌ {value}: format invalide (attendu: BYXX)")
                all_passed = False
        
    except Exception as e:
        print(f"   ❌ Erreur test dropdown: {e}")
        all_passed = False
    
    return all_passed

def test_edge_cases():
    """Test des cas limites"""
    print("\n5️⃣ TEST CAS LIMITES")
    
    edge_cases = [
        # (date, expected_byxx, description)
        ('2024-04-30', 'BY24', 'Dernier jour période fiscale'),
        ('2024-05-01', 'BY25', 'Premier jour période fiscale'),
        ('2024-12-31', 'BY25', 'Fin année civile'),
        ('2025-01-01', 'BY25', 'Début année civile'),
        ('2025-04-30', 'BY25', 'Fin période fiscale suivante'),
        ('2025-05-01', 'BY26', 'Début période suivante'),
    ]
    
    all_passed = True
    
    print("   📅 Tests dates critiques:")
    for date_str, expected_byxx, description in edge_cases:
        try:
            result = get_fiscal_year_from_date(date_str)
            passed = result == expected_byxx
            status = "✅" if passed else "❌"
            print(f"      {status} {date_str}: {result} (attendu: {expected_byxx}) - {description}")
            if not passed:
                all_passed = False
        except Exception as e:
            print(f"      ❌ {date_str}: erreur ({e})")
            all_passed = False
    
    return all_passed

def test_consistency():
    """Test de cohérence globale"""
    print("\n6️⃣ TEST COHÉRENCE GLOBALE")
    
    all_passed = True
    
    # Test logique métier
    print("   🎯 Logique métier:")
    by25_year = byxx_to_year('BY25')
    if by25_year == 2024:
        print("      ✅ BY25 correspond à période Mai 2024 - Avril 2025")
    else:
        print(f"      ❌ BY25 donne {by25_year} (attendu: 2024)")
        all_passed = False
    
    # Test années futures
    print("   🔮 Années futures:")
    current_year = datetime.now().year
    future_years = [current_year + i for i in range(1, 4)]
    
    for year in future_years:
        byxx = year_to_byxx(year)
        back_year = byxx_to_year(byxx) if byxx else None
        passed = back_year == year
        status = "✅" if passed else "❌"
        print(f"      {status} {year} ↔ {byxx} ↔ {back_year}")
        if not passed:
            all_passed = False
    
    return all_passed

if __name__ == "__main__":
    print("🚀 DÉMARRAGE VALIDATION SYSTÈME ANNÉES FISCALES")
    print(f"📅 Date d'exécution: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Initialiser la base de données
        db.init_database()
        
        # Exécuter la validation
        success = main()
        
        # Code de sortie
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"\n❌ ERREUR FATALE: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)
