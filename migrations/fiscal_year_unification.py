"""
Migration pour unifier la gestion des années fiscales
Supprime l'utilisation de fiscal_year (int) et utilise uniquement by (string) depuis les dropdowns
"""

from models.database import db

def migrate_fiscal_year_unification():
    """Unifie la gestion des années fiscales"""
    try:
        print("🔄 Migration unification années fiscales...")
        
        # 1. Vérifier si la colonne fiscal_year existe
        if db.column_exists('demandes', 'fiscal_year'):
            # 2. Mettre à jour les demandes existantes qui ont fiscal_year mais pas by
            print("📝 Mise à jour des demandes existantes...")
            
            # Récupérer les demandes avec fiscal_year mais sans by
            demandes_to_update = db.execute_query("""
                SELECT id, fiscal_year 
                FROM demandes 
                WHERE fiscal_year IS NOT NULL 
                AND (by IS NULL OR by = '')
            """, fetch='all')
            
            # Mettre à jour chaque demande
            for demande in demandes_to_update or []:
                fiscal_year = demande['fiscal_year']
                if fiscal_year and fiscal_year >= 1000:  # Validation basique
                    by_value = f"BY{str(fiscal_year)[2:]}"
                    db.execute_query("""
                        UPDATE demandes 
                        SET by = ?
                        WHERE id = ?
                    """, (by_value, demande['id']))
                    print(f"  ✅ Demande {demande['id']}: fiscal_year {fiscal_year} → by {by_value}")
        
        # 3. S'assurer que toutes les demandes ont une année fiscale par défaut
        from datetime import datetime
        current_year = datetime.now().year
        default_by = f"BY{str(current_year)[2:]}"
        
        updated_count = db.execute_query("""
            UPDATE demandes 
            SET by = ?
            WHERE by IS NULL OR by = ''
        """, (default_by,))
        
        if updated_count > 0:
            print(f"📝 {updated_count} demandes mises à jour avec l'année par défaut: {default_by}")
        
        # 4. Vérifier les options d'années fiscales dans dropdown_options
        existing_years = db.execute_query("""
            SELECT COUNT(*) as count
            FROM dropdown_options 
            WHERE category = 'annee_fiscale' AND is_active = TRUE
        """, fetch='one')
        
        if not existing_years or existing_years['count'] == 0:
            print("📋 Création des années fiscales par défaut...")
            # Créer quelques années fiscales par défaut avec le BON format
            default_years = [
                ('BY23', 'BY23', 1),
                ('BY24', 'BY24', 2), 
                ('BY25', 'BY25', 3),
                ('BY26', 'BY26', 4),
                ('BY27', 'BY27', 5),
            ]
            
            for value, label, order_index in default_years:
                db.execute_query("""
                    INSERT OR IGNORE INTO dropdown_options 
                    (category, value, label, order_index, is_active)
                    VALUES (?, ?, ?, ?, TRUE)
                """, ('annee_fiscale', value, label, order_index))
            
            print(f"✅ {len(default_years)} années fiscales créées")
        else:
            # Corriger les années existantes avec mauvais format
            print("🔧 Correction des années fiscales existantes...")
            
            wrong_years = db.execute_query("""
                SELECT id, value, label
                FROM dropdown_options 
                WHERE category = 'annee_fiscale' 
                AND value NOT LIKE 'BY%'
            """, fetch='all')
            
            for year in wrong_years or []:
                # Corriger le format: by25 → BY25
                old_value = year['value']
                if old_value.startswith('by') and len(old_value) == 4:
                    new_value = old_value.upper()  # by25 → BY25
                    
                    # Mettre à jour la valeur
                    db.execute_query("""
                        UPDATE dropdown_options 
                        SET value = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE id = ?
                    """, (new_value, year['id']))
                    
                    # Mettre à jour les demandes qui utilisent cette valeur
                    update_count = db.execute_query("""
                        UPDATE demandes 
                        SET by = ?
                        WHERE by = ?
                    """, (new_value, old_value))
                    
                    print(f"  ✅ {old_value} → {new_value} ({update_count} demandes mises à jour)")
        
        print("✅ Migration années fiscales terminée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur migration années fiscales: {e}")
        import traceback
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    migrate_fiscal_year_unification()
