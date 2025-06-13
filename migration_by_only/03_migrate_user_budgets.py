#!/usr/bin/env python3
"""
Script de migration de user_budgets vers format BY uniquement
Migre de fiscal_year (int) vers by (string)
"""
import sys
import os
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def migrate_user_budgets_to_by():
    """Migration user_budgets vers format BY"""
    print("🔄 MIGRATION USER_BUDGETS - fiscal_year → by")
    print("=" * 50)
    
    try:
        from models.database import db
        
        # 1. Vérifier l'état actuel
        print("📋 1. VÉRIFICATION ÉTAT ACTUEL")
        print("-" * 30)
        
        if not db.table_exists('user_budgets'):
            print("❌ Table user_budgets n'existe pas")
            return False
        
        # Compter budgets existants
        total_budgets = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')['count']
        print(f"📊 Total budgets: {total_budgets}")
        
        if total_budgets == 0:
            print("✅ Aucun budget à migrer")
            return True
        
        # Vérifier colonnes existantes
        has_fiscal_year = db.column_exists('user_budgets', 'fiscal_year')
        has_by = db.column_exists('user_budgets', 'by')
        
        print(f"📋 Colonne fiscal_year: {'✅' if has_fiscal_year else '❌'}")
        print(f"📋 Colonne by: {'✅' if has_by else '❌'}")
        
        # 2. Ajouter colonne by si nécessaire
        print(f"\n📋 2. PRÉPARATION STRUCTURE")
        print("-" * 30)
        
        if not has_by:
            print("➕ Ajout colonne 'by' à user_budgets...")
            db.execute_query("ALTER TABLE user_budgets ADD COLUMN by TEXT")
            print("✅ Colonne 'by' ajoutée")
        else:
            print("✅ Colonne 'by' existe déjà")
        
        # 3. Migration des données
        print(f"\n📋 3. MIGRATION DONNÉES")
        print("-" * 30)
        
        if has_fiscal_year:
            # Récupérer budgets avec fiscal_year mais sans by
            budgets_to_migrate = db.execute_query("""
                SELECT id, user_id, fiscal_year, allocated_budget
                FROM user_budgets 
                WHERE fiscal_year IS NOT NULL 
                AND (by IS NULL OR by = '')
            """, fetch='all')
            
            if budgets_to_migrate:
                print(f"🔄 Migration de {len(budgets_to_migrate)} budget(s)...")
                
                migrated_count = 0
                error_count = 0
                
                for budget in budgets_to_migrate:
                    try:
                        fiscal_year = budget['fiscal_year']
                        
                        # Convertir 2025 → BY25, 2024 → BY24
                        if fiscal_year and fiscal_year >= 1000:
                            by_value = f"BY{str(fiscal_year)[2:]}"  # 2025 → BY25
                            
                            # Mettre à jour
                            db.execute_query("""
                                UPDATE user_budgets 
                                SET by = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE id = ?
                            """, (by_value, budget['id']))
                            
                            migrated_count += 1
                            print(f"  ✅ Budget {budget['id']}: {fiscal_year} → {by_value} (User {budget['user_id']}, {budget['allocated_budget']:,.0f}€)")
                        else:
                            print(f"  ⚠️ Budget {budget['id']}: fiscal_year invalide ({fiscal_year})")
                            error_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        print(f"  ❌ Erreur budget {budget['id']}: {e}")
                
                print(f"\n📊 Résultat migration:")
                print(f"   ✅ Migrés: {migrated_count}")
                print(f"   ❌ Erreurs: {error_count}")
                
            else:
                print("✅ Aucun budget à migrer (déjà fait ou pas de fiscal_year)")
        
        # 4. Assurer que tous les budgets ont une année by
        print(f"\n📋 4. VALIDATION ET NETTOYAGE")
        print("-" * 30)
        
        # Compter budgets sans by
        missing_by = db.execute_query("""
            SELECT COUNT(*) as count FROM user_budgets 
            WHERE by IS NULL OR by = ''
        """, fetch='one')['count']
        
        if missing_by > 0:
            print(f"⚠️ {missing_by} budget(s) sans année fiscale 'by'")
            
            # Option: assigner année par défaut
            from utils.fiscal_year_utils import get_default_fiscal_year
            default_by = get_default_fiscal_year()
            
            print(f"🔧 Attribution année par défaut: {default_by}")
            db.execute_query("""
                UPDATE user_budgets 
                SET by = ?, updated_at = CURRENT_TIMESTAMP
                WHERE by IS NULL OR by = ''
            """, (default_by,))
            print(f"✅ {missing_by} budget(s) mis à jour avec {default_by}")
        
        # 5. Vérification finale
        print(f"\n📋 5. VÉRIFICATION FINALE")
        print("-" * 30)
        
        # Compter par année by
        by_stats = db.execute_query("""
            SELECT by, COUNT(*) as count, SUM(allocated_budget) as total_budget
            FROM user_budgets 
            WHERE by IS NOT NULL AND by != ''
            GROUP BY by 
            ORDER BY by
        """, fetch='all')
        
        if by_stats:
            print("📊 Répartition finale par année fiscale (BY):")
            total_final_budgets = 0
            total_final_amount = 0
            
            for stat in by_stats:
                count = stat['count']
                amount = stat['total_budget'] or 0
                total_final_budgets += count
                total_final_amount += amount
                print(f"   {stat['by']}: {count} budget(s), {amount:,.0f}€")
            
            print(f"\n📊 TOTAUX:")
            print(f"   Budgets: {total_final_budgets}")
            print(f"   Montant: {total_final_amount:,.0f}€")
            
            # Vérifier cohérence
            if total_final_budgets == total_budgets:
                print("✅ Migration cohérente - tous les budgets ont une année BY")
            else:
                print(f"⚠️ Incohérence détectée: {total_budgets} → {total_final_budgets}")
        
        # 6. Tester compatibilité avec dropdowns
        print(f"\n📋 6. COMPATIBILITÉ DROPDOWNS")
        print("-" * 30)
        
        # Vérifier que les années BY utilisées existent dans dropdown_options
        if db.table_exists('dropdown_options'):
            valid_years = db.execute_query("""
                SELECT value FROM dropdown_options 
                WHERE category = 'annee_fiscale' AND is_active = TRUE
            """, fetch='all')
            
            valid_year_values = {row['value'] for row in valid_years} if valid_years else set()
            
            used_years = db.execute_query("""
                SELECT DISTINCT by FROM user_budgets 
                WHERE by IS NOT NULL AND by != ''
            """, fetch='all')
            
            used_year_values = {row['by'] for row in used_years} if used_years else set()
            
            print(f"📋 Années valides (dropdowns): {sorted(valid_year_values)}")
            print(f"📋 Années utilisées (budgets): {sorted(used_year_values)}")
            
            # Années manquantes dans dropdowns
            missing_in_dropdowns = used_year_values - valid_year_values
            if missing_in_dropdowns:
                print(f"⚠️ Années manquantes dans dropdowns: {sorted(missing_in_dropdowns)}")
                print("💡 Suggestion: Ajouter ces années dans admin > Listes Déroulantes")
            else:
                print("✅ Toutes les années utilisées sont valides")
        
        print(f"\n✅ Migration user_budgets terminée - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_migration():
    """Tests post-migration"""
    print("\n🧪 TESTS POST-MIGRATION")
    print("-" * 30)
    
    try:
        from models.database import db
        
        # Test 1: Tous les budgets ont une année BY
        no_by = db.execute_query("""
            SELECT COUNT(*) as count FROM user_budgets 
            WHERE by IS NULL OR by = ''
        """, fetch='one')['count']
        
        if no_by == 0:
            print("✅ Test 1: Tous les budgets ont une année BY")
        else:
            print(f"❌ Test 1: {no_by} budget(s) sans année BY")
        
        # Test 2: Format BY correct
        bad_format = db.execute_query("""
            SELECT COUNT(*) as count FROM user_budgets 
            WHERE by IS NOT NULL AND by != '' AND by NOT LIKE 'BY%'
        """, fetch='one')['count']
        
        if bad_format == 0:
            print("✅ Test 2: Format BY correct pour tous les budgets")
        else:
            print(f"❌ Test 2: {bad_format} budget(s) avec mauvais format")
        
        # Test 3: Longueur BY
        bad_length = db.execute_query("""
            SELECT COUNT(*) as count FROM user_budgets 
            WHERE by IS NOT NULL AND by != '' AND LENGTH(by) != 4
        """, fetch='one')['count']
        
        if bad_length == 0:
            print("✅ Test 3: Longueur BY correcte (4 caractères)")
        else:
            print(f"❌ Test 3: {bad_length} budget(s) avec mauvaise longueur")
        
        return no_by == 0 and bad_format == 0 and bad_length == 0
        
    except Exception as e:
        print(f"❌ Erreur tests: {e}")
        return False

if __name__ == "__main__":
    print("🔄 MIGRATION USER_BUDGETS TO BY")
    print("=" * 50)
    
    # Migration
    success = migrate_user_budgets_to_by()
    
    if success:
        # Tests
        tests_ok = test_migration()
        
        print(f"\n{'='*50}")
        if tests_ok:
            print("🎉 Migration et tests réussis!")
            print("Prochaine étape: python migration_by_only/04_update_user_budget_model.py")
        else:
            print("⚠️ Migration OK mais tests échoués")
            print("Vérifiez les données avant de continuer")
    else:
        print(f"\n{'='*50}")
        print("💥 Migration échouée!")
        print("❌ ARRÊT - Restaurer backup si nécessaire")
    
    exit(0 if success and (not 'tests_ok' in locals() or tests_ok) else 1)
