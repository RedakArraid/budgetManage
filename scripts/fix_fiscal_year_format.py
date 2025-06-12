#!/usr/bin/env python3
"""
Script de correction pour les années fiscales avec mauvais format
Corrige by25 → BY25 dans les dropdowns et les demandes
"""
import sys
import os

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def fix_fiscal_year_format():
    """Corrige le format des années fiscales dans la base de données"""
    print("🔧 Correction format années fiscales...")
    
    try:
        from models.database import db
        
        # 1. Identifier les années avec mauvais format
        wrong_years = db.execute_query("""
            SELECT id, value, label, is_active
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' 
            AND value NOT LIKE 'BY%'
        """, fetch='all')
        
        if not wrong_years:
            print("✅ Aucune correction nécessaire - toutes les années ont le bon format")
            return True
        
        print(f"🔍 {len(wrong_years)} année(s) à corriger trouvée(s):")
        for year in wrong_years:
            print(f"  - ID {year['id']}: '{year['value']}' (label: '{year['label']}')")
        
        # 2. Corriger chaque année
        corrections = []
        
        for year in wrong_years:
            old_value = year['value']
            
            # Générer la nouvelle valeur
            if old_value.startswith('by') and len(old_value) == 4:
                new_value = old_value.upper()  # by25 → BY25
            elif old_value.isdigit() and len(old_value) == 4:
                new_value = f"BY{old_value[2:]}"  # 2025 → BY25
            elif old_value.isdigit() and len(old_value) == 2:
                new_value = f"BY{old_value}"  # 25 → BY25
            else:
                print(f"⚠️ Format non reconnu pour '{old_value}' - ignoré")
                continue
            
            corrections.append((year['id'], old_value, new_value, year['label']))
        
        if not corrections:
            print("⚠️ Aucune correction applicable")
            return True
        
        print(f"\n🔄 Application de {len(corrections)} correction(s):")
        
        # 3. Appliquer les corrections
        for year_id, old_value, new_value, label in corrections:
            try:
                # Vérifier qu'il n'y a pas de conflit
                existing = db.execute_query("""
                    SELECT id FROM dropdown_options
                    WHERE category = 'annee_fiscale' AND value = ? AND id != ?
                """, (new_value, year_id), fetch='one')
                
                if existing:
                    print(f"  ❌ Conflit pour '{new_value}' (existe déjà) - ignoré")
                    continue
                
                # Mettre à jour la dropdown option
                db.execute_query("""
                    UPDATE dropdown_options 
                    SET value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_value, year_id))
                
                # Compter les demandes affectées
                demandes_count = db.execute_query("""
                    SELECT COUNT(*) as count FROM demandes WHERE by = ?
                """, (old_value,), fetch='one')
                
                count = demandes_count['count'] if demandes_count else 0
                
                # Mettre à jour les demandes
                if count > 0:
                    db.execute_query("""
                        UPDATE demandes 
                        SET by = ?
                        WHERE by = ?
                    """, (new_value, old_value))
                
                print(f"  ✅ '{old_value}' → '{new_value}' ({count} demande(s) mise(s) à jour)")
                
            except Exception as e:
                print(f"  ❌ Erreur correction '{old_value}': {e}")
        
        # 4. Vérification finale
        print(f"\n🔍 Vérification finale...")
        
        remaining_wrong = db.execute_query("""
            SELECT COUNT(*) as count
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' 
            AND value NOT LIKE 'BY%'
        """, fetch='one')
        
        wrong_count = remaining_wrong['count'] if remaining_wrong else 0
        
        if wrong_count == 0:
            print("✅ Toutes les années fiscales ont maintenant le bon format!")
        else:
            print(f"⚠️ {wrong_count} année(s) avec format incorrect restante(s)")
        
        # Afficher l'état final
        all_years = db.execute_query("""
            SELECT value, label, is_active
            FROM dropdown_options 
            WHERE category = 'annee_fiscale'
            ORDER BY value
        """, fetch='all')
        
        print(f"\n📋 État final ({len(all_years)} année(s)):")
        for year in all_years:
            status = "✅" if year['is_active'] else "❌"
            format_ok = "✅" if year['value'].startswith('BY') else "❌"
            print(f"  {status} {format_ok} {year['value']} ({year['label']})")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur correction: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_fiscal_year_format()
    if success:
        print("\n🎉 Correction terminée avec succès!")
        print("Vous pouvez maintenant relancer les tests:")
        print("  python scripts/test_fiscal_year_fix.py")
    else:
        print("\n💥 Correction échouée!")
    
    exit(0 if success else 1)
