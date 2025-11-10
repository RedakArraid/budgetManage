#!/usr/bin/env python3
"""
Script de correction FINAL avec la vraie logique d'année fiscale
LOGIQUE MÉTIER: BY25 = Mai 2024 à Avril 2025
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from utils.fiscal_year_utils import get_fiscal_year_display

def correct_existing_dropdown_labels():
    """Corrige les labels des années fiscales déjà créées avec la vraie logique"""
    try:
        print("🔧 CORRECTION DES LABELS AVEC VRAIE LOGIQUE FISCALE")
        print("=" * 55)
        print("📋 LOGIQUE: BY25 = Mai 2024 à Avril 2025")
        print()
        
        # Récupérer les années existantes
        existing_years = db.execute_query("""
            SELECT id, value, label 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if not existing_years:
            print("❌ Aucune année fiscale trouvée")
            return False
        
        print(f"📊 {len(existing_years)} années trouvées à corriger:")
        
        corrections = []
        for year in existing_years:
            old_label = year['label']
            # Générer le nouveau label avec la vraie logique
            new_label = get_fiscal_year_display(year['value'])
            
            if old_label != new_label:
                corrections.append({
                    'id': year['id'],
                    'value': year['value'],
                    'old_label': old_label,
                    'new_label': new_label
                })
                print(f"   📝 {year['value']}: '{old_label}' → '{new_label}'")
        
        if not corrections:
            print("✅ Tous les labels sont déjà corrects!")
            return True
        
        print(f"\n🔄 Application de {len(corrections)} corrections...")
        
        success_count = 0
        for correction in corrections:
            try:
                db.execute_query("""
                    UPDATE dropdown_options 
                    SET label = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (correction['new_label'], correction['id']))
                
                success_count += 1
                print(f"   ✅ {correction['value']}: Corrigé")
                
            except Exception as e:
                print(f"   ❌ {correction['value']}: Erreur - {e}")
        
        print(f"\n📊 Résultats: {success_count}/{len(corrections)} corrections appliquées")
        return success_count == len(corrections)
        
    except Exception as e:
        print(f"❌ Erreur correction labels: {e}")
        return False

def verify_conversion_logic():
    """Vérifie que la logique de conversion est correcte"""
    print(f"\n🧪 VÉRIFICATION LOGIQUE DE CONVERSION")
    print("=" * 40)
    
    from utils.fiscal_year_utils import byxx_to_year, year_to_byxx
    
    # Tests critiques
    test_cases = [
        # (byxx, année_début_attendue, description)
        ("BY25", 2024, "BY25 doit commencer en Mai 2024"),
        ("BY24", 2023, "BY24 doit commencer en Mai 2023"),
        ("BY26", 2025, "BY26 doit commencer en Mai 2025"),
    ]
    
    all_correct = True
    for byxx, expected_start, description in test_cases:
        actual_start = byxx_to_year(byxx)
        
        if actual_start == expected_start:
            print(f"   ✅ {byxx} → {actual_start} ({description})")
        else:
            print(f"   ❌ {byxx} → {actual_start} (attendu: {expected_start}) - {description}")
            all_correct = False
    
    # Tests de conversion inverse
    print(f"\n🔄 Tests conversion inverse:")
    reverse_tests = [
        (2024, "BY25", "2024 (début) doit donner BY25"),
        (2023, "BY24", "2023 (début) doit donner BY24"),
        (2025, "BY26", "2025 (début) doit donner BY26"),
    ]
    
    for start_year, expected_byxx, description in reverse_tests:
        actual_byxx = year_to_byxx(start_year)
        
        if actual_byxx == expected_byxx:
            print(f"   ✅ {start_year} → {actual_byxx} ({description})")
        else:
            print(f"   ❌ {start_year} → {actual_byxx} (attendu: {expected_byxx}) - {description}")
            all_correct = False
    
    return all_correct

def show_final_state():
    """Affiche l'état final des années fiscales"""
    print(f"\n📋 ÉTAT FINAL DES ANNÉES FISCALES")
    print("=" * 40)
    
    try:
        years = db.execute_query("""
            SELECT value, label, is_active 
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        if years:
            print("📊 Années fiscales configurées:")
            for year in years:
                status = "🟢" if year['is_active'] else "🔴"
                print(f"   {status} {year['value']} → {year['label']}")
            
            print(f"\n💡 RAPPEL DE LA LOGIQUE:")
            print(f"   • BY25 = Période fiscale Mai 2024 → Avril 2025")
            print(f"   • BY24 = Période fiscale Mai 2023 → Avril 2024") 
            print(f"   • BY26 = Période fiscale Mai 2025 → Avril 2026")
            print(f"   • L'année fiscale commence toujours en Mai")
            
        else:
            print("❌ Aucune année fiscale configurée")
            
    except Exception as e:
        print(f"❌ Erreur affichage état final: {e}")

def main():
    """Fonction principale de correction finale"""
    print("🎯 CORRECTION FINALE - VRAIE LOGIQUE ANNÉE FISCALE")
    print("=" * 60)
    print("📋 LOGIQUE MÉTIER: BY25 = Mai 2024 à Avril 2025")
    print("🎯 Objectif: Corriger tous les labels avec la vraie période")
    print()
    
    try:
        # Étape 1: Vérifier la logique de conversion
        print("🧪 ÉTAPE 1: Vérification logique de conversion")
        print("-" * 45)
        
        conversion_ok = verify_conversion_logic()
        if not conversion_ok:
            print("❌ Problème dans la logique de conversion!")
            return False
        
        # Étape 2: Corriger les labels existants
        print(f"\n🔧 ÉTAPE 2: Correction des labels existants")
        print("-" * 40)
        
        labels_ok = correct_existing_dropdown_labels()
        
        # Étape 3: Afficher l'état final
        show_final_state()
        
        # Résumé final
        print(f"\n" + "=" * 60)
        if conversion_ok and labels_ok:
            print("🎉 CORRECTION FINALE TERMINÉE AVEC SUCCÈS!")
            print("\n✅ SYSTÈME CORRIGÉ:")
            print("   • Logique de conversion: BY25 = Mai 2024 → Avril 2025 ✅")
            print("   • Labels dropdown: Période complète affichée ✅")
            print("   • Interface: Conversion automatique BYXX ↔ année ✅")
            
            print(f"\n🚀 PROCHAINES ÉTAPES:")
            print("   1. Redémarrez votre application Streamlit")
            print("   2. Testez la page 'Gestion Budgets'")
            print("   3. Vérifiez que les années s'affichent correctement:")
            print("      - BY25 (Mai 2024 - Avril 2025)")
            print("      - BY24 (Mai 2023 - Avril 2024)")
            print("      - etc.")
            
            print(f"\n📋 COMPRÉHENSION CONFIRMÉE:")
            print("   • Année fiscale ≠ Année civile")
            print("   • BY25 commence en Mai 2024 (pas 2025)")
            print("   • Période: Mai N-1 à Avril N")
            
        else:
            print("⚠️ CORRECTION PARTIELLE")
            print("   Certaines étapes ont échoué, vérifiez les erreurs ci-dessus")
        
        return conversion_ok and labels_ok
        
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Démarrage de la correction finale...")
    success = main()
    
    if success:
        print(f"\n💡 NOTE IMPORTANTE:")
        print(f"   La logique métier est maintenant correctement implémentée.")
        print(f"   BY25 = Mai 2024 à Avril 2025 (année fiscale 2024-2025)")
        print(f"   Les utilisateurs verront les vraies périodes dans l'interface.")
    
    sys.exit(0 if success else 1)
