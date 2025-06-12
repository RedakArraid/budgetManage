#!/usr/bin/env python3
"""
Script de correction forcée pour les années fiscales
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def force_fix_fiscal_years():
    """Force la correction des années fiscales"""
    print("🔧 Correction FORCÉE des années fiscales...")
    
    try:
        from models.database import db
        
        # 1. Supprimer toutes les années fiscales existantes
        print("🗑️ Suppression des années fiscales existantes...")
        deleted_count = db.execute_query("""
            DELETE FROM dropdown_options WHERE category = 'annee_fiscale'
        """)
        print(f"✅ {deleted_count} année(s) supprimée(s)")
        
        # 2. Créer les bonnes années fiscales
        print("➕ Création des nouvelles années fiscales...")
        
        good_years = [
            ('BY23', 'BY23', 1),
            ('BY24', 'BY24', 2), 
            ('BY25', 'BY25', 3),
            ('BY26', 'BY26', 4),
            ('BY27', 'BY27', 5),
        ]
        
        for value, label, order_index in good_years:
            db.execute_query("""
                INSERT INTO dropdown_options 
                (category, value, label, order_index, is_active, created_at, updated_at)
                VALUES (?, ?, ?, ?, TRUE, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """, ('annee_fiscale', value, label, order_index))
            print(f"  ✅ Créé: {value} ({label})")
        
        # 3. Mettre à jour les demandes avec mauvaises valeurs
        print("🔄 Correction des demandes existantes...")
        
        corrections = [
            ('by23', 'BY23'),
            ('by24', 'BY24'),
            ('by25', 'BY25'),
            ('by26', 'BY26'),
            ('by27', 'BY27'),
            ('2023', 'BY23'),
            ('2024', 'BY24'),
            ('2025', 'BY25'),
            ('2026', 'BY26'),
            ('2027', 'BY27'),
        ]
        
        total_updated = 0
        for old_value, new_value in corrections:
            count = db.execute_query("""
                UPDATE demandes SET by = ? WHERE by = ?
            """, (new_value, old_value))
            if count > 0:
                print(f"  ✅ {old_value} → {new_value} : {count} demande(s)")
                total_updated += count
        
        print(f"✅ Total: {total_updated} demande(s) corrigée(s)")
        
        # 4. Vérification finale
        print("🔍 Vérification finale...")
        
        final_years = db.execute_query("""
            SELECT value, label, is_active
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY order_index
        """, fetch='all')
        
        print(f"📋 Années fiscales finales ({len(final_years)}):")
        for year in final_years:
            status = "✅" if year['is_active'] else "❌"
            format_ok = "✅" if year['value'].startswith('BY') else "❌"
            print(f"  {status} {format_ok} {year['value']} → '{year['label']}'")
        
        # Test des utilitaires
        print("\n🧪 Test des utilitaires après correction...")
        from utils.fiscal_year_utils import get_valid_fiscal_years, get_default_fiscal_year
        
        valid_years = get_valid_fiscal_years()
        print(f"get_valid_fiscal_years(): {valid_years}")
        
        default_year = get_default_fiscal_year()
        print(f"get_default_fiscal_year(): {repr(default_year)}")
        print(f"Commence par BY: {default_year.startswith('BY') if default_year else False}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction forcée: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = force_fix_fiscal_years()
    if success:
        print("\n🎉 Correction forcée terminée!")
        print("Relancez les tests:")
        print("  python scripts/test_fiscal_year_fix.py")
    else:
        print("\n💥 Correction forcée échouée!")
    
    exit(0 if success else 1)
