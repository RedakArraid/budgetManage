#!/usr/bin/env python3
"""
Script d'audit de l'état actuel avant migration vers format BY uniquement
Analyse tous les usages de fiscal_year dans la base de données
"""
import sys
import os
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def audit_current_state():
    """Audit complet de l'état actuel avant migration"""
    print("🔍 AUDIT - État actuel avant migration vers BY uniquement")
    print("=" * 60)
    
    try:
        from models.database import db
        
        # 1. Structure des tables
        print("\n📋 1. STRUCTURE DES TABLES")
        print("-" * 30)
        
        # Vérifier table user_budgets
        if db.table_exists('user_budgets'):
            columns = db.execute_query("PRAGMA table_info(user_budgets)", fetch='all')
            print("✅ Table user_budgets existe:")
            for col in columns:
                print(f"   - {col[1]} {col[2]} {'(PK)' if col[5] else ''}")
        else:
            print("❌ Table user_budgets n'existe pas")
        
        # Vérifier table demandes
        if db.table_exists('demandes'):
            columns = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
            fiscal_cols = [col for col in columns if 'fiscal' in col[1].lower() or col[1] in ['cy', 'by']]
            print("\n✅ Table demandes - Colonnes années fiscales:")
            for col in fiscal_cols:
                print(f"   - {col[1]} {col[2]}")
        
        # 2. Données existantes user_budgets
        print("\n💰 2. DONNÉES USER_BUDGETS")
        print("-" * 30)
        
        if db.table_exists('user_budgets'):
            # Compter les budgets totaux
            total_budgets = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')
            print(f"📊 Total budgets: {total_budgets['count']}")
            
            # Budgets par année fiscal_year
            if db.column_exists('user_budgets', 'fiscal_year'):
                by_year = db.execute_query("""
                    SELECT fiscal_year, COUNT(*) as count, SUM(allocated_budget) as total_budget
                    FROM user_budgets 
                    WHERE fiscal_year IS NOT NULL
                    GROUP BY fiscal_year 
                    ORDER BY fiscal_year
                """, fetch='all')
                
                print("📅 Répartition par fiscal_year (INTEGER):")
                for row in by_year:
                    print(f"   - {row['fiscal_year']}: {row['count']} budget(s), {row['total_budget']:,.0f}€")
            
            # Budgets par colonne by (si elle existe)
            if db.column_exists('user_budgets', 'by'):
                by_by = db.execute_query("""
                    SELECT by, COUNT(*) as count, SUM(allocated_budget) as total_budget
                    FROM user_budgets 
                    WHERE by IS NOT NULL AND by != ''
                    GROUP BY by 
                    ORDER BY by
                """, fetch='all')
                
                if by_by:
                    print("📅 Répartition par by (STRING):")
                    for row in by_by:
                        print(f"   - {row['by']}: {row['count']} budget(s), {row['total_budget']:,.0f}€")
                else:
                    print("⚠️ Colonne 'by' existe mais aucune donnée")
            else:
                print("❌ Colonne 'by' n'existe pas dans user_budgets")
        
        # 3. Données demandes
        print("\n📋 3. DONNÉES DEMANDES")
        print("-" * 30)
        
        if db.table_exists('demandes'):
            total_demandes = db.execute_query("SELECT COUNT(*) as count FROM demandes", fetch='one')
            print(f"📊 Total demandes: {total_demandes['count']}")
            
            # Demandes par colonne by
            if db.column_exists('demandes', 'by'):
                by_by = db.execute_query("""
                    SELECT by, COUNT(*) as count, SUM(montant) as total_montant
                    FROM demandes 
                    WHERE by IS NOT NULL AND by != ''
                    GROUP BY by 
                    ORDER BY by
                """, fetch='all')
                
                if by_by:
                    print("📅 Demandes par by (STRING):")
                    for row in by_by:
                        print(f"   - {row['by']}: {row['count']} demande(s), {row['total_montant']:,.0f}€")
                else:
                    print("⚠️ Colonne 'by' existe mais aucune donnée")
            
            # Demandes par fiscal_year (si elle existe)
            if db.column_exists('demandes', 'fiscal_year'):
                by_fy = db.execute_query("""
                    SELECT fiscal_year, COUNT(*) as count, SUM(montant) as total_montant
                    FROM demandes 
                    WHERE fiscal_year IS NOT NULL
                    GROUP BY fiscal_year 
                    ORDER BY fiscal_year
                """, fetch='all')
                
                if by_fy:
                    print("📅 Demandes par fiscal_year (INTEGER):")
                    for row in by_fy:
                        print(f"   - {row['fiscal_year']}: {row['count']} demande(s), {row['total_montant']:,.0f}€")
                else:
                    print("⚠️ Colonne 'fiscal_year' existe mais aucune donnée")
        
        # 4. Options années fiscales
        print("\n📋 4. OPTIONS ANNÉES FISCALES")
        print("-" * 30)
        
        if db.table_exists('dropdown_options'):
            fiscal_options = db.execute_query("""
                SELECT value, label, is_active, order_index
                FROM dropdown_options 
                WHERE category = 'annee_fiscale'
                ORDER BY order_index, value
            """, fetch='all')
            
            if fiscal_options:
                print("📋 Années fiscales configurées:")
                for opt in fiscal_options:
                    status = "✅" if opt['is_active'] else "❌"
                    format_ok = "✅" if opt['value'].startswith('BY') else "❌"
                    print(f"   {status} {format_ok} {opt['value']} ({opt['label']}) - ordre: {opt['order_index']}")
            else:
                print("❌ Aucune année fiscale configurée")
        
        # 5. Incohérences détectées
        print("\n🚨 5. INCOHÉRENCES DÉTECTÉES")
        print("-" * 30)
        
        issues = []
        
        # Vérifier user_budgets sans colonne by
        if db.table_exists('user_budgets') and not db.column_exists('user_budgets', 'by'):
            budget_count = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')['count']
            if budget_count > 0:
                issues.append(f"❌ {budget_count} budget(s) utilisent fiscal_year (int) au lieu de by (string)")
        
        # Vérifier demandes avec fiscal_year mais sans by
        if db.table_exists('demandes') and db.column_exists('demandes', 'fiscal_year'):
            missing_by = db.execute_query("""
                SELECT COUNT(*) as count FROM demandes 
                WHERE fiscal_year IS NOT NULL AND (by IS NULL OR by = '')
            """, fetch='one')['count']
            if missing_by > 0:
                issues.append(f"⚠️ {missing_by} demande(s) ont fiscal_year mais pas by")
        
        # Vérifier années fiscales avec mauvais format
        if db.table_exists('dropdown_options'):
            bad_format = db.execute_query("""
                SELECT COUNT(*) as count FROM dropdown_options 
                WHERE category = 'annee_fiscale' AND value NOT LIKE 'BY%'
            """, fetch='one')['count']
            if bad_format > 0:
                issues.append(f"⚠️ {bad_format} année(s) fiscale(s) avec mauvais format dans dropdown_options")
        
        if issues:
            for issue in issues:
                print(issue)
        else:
            print("✅ Aucune incohérence majeure détectée")
        
        # 6. Plan de migration recommandé
        print("\n📋 6. PLAN DE MIGRATION RECOMMANDÉ")
        print("-" * 30)
        
        migration_steps = []
        
        if db.table_exists('user_budgets'):
            if not db.column_exists('user_budgets', 'by'):
                migration_steps.append("1. Ajouter colonne 'by' à user_budgets")
                migration_steps.append("2. Migrer données fiscal_year → by dans user_budgets")
            
            budget_count = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')['count']
            if budget_count > 0:
                migration_steps.append("3. Modifier UserBudgetModel pour utiliser by au lieu de fiscal_year")
        
        if db.table_exists('demandes') and db.column_exists('demandes', 'fiscal_year'):
            migration_steps.append("4. Nettoyer allowed_fields dans DemandeModel")
            migration_steps.append("5. Simplifier fonction calculate_cy_by()")
        
        migration_steps.append("6. Nettoyer dataclass Demande (supprimer fy)")
        migration_steps.append("7. Mettre à jour gestion_budgets_view.py")
        migration_steps.append("8. Tests de validation")
        
        for step in migration_steps:
            print(f"   {step}")
        
        # 7. Résumé
        print("\n📊 7. RÉSUMÉ AUDIT")
        print("-" * 30)
        
        total_user_budgets = 0
        total_demandes = 0
        
        if db.table_exists('user_budgets'):
            total_user_budgets = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')['count']
        
        if db.table_exists('demandes'):
            total_demandes = db.execute_query("SELECT COUNT(*) as count FROM demandes", fetch='one')['count']
        
        print(f"📊 Données à migrer:")
        print(f"   - {total_user_budgets} budget(s) utilisateur")
        print(f"   - {total_demandes} demande(s)")
        print(f"   - {len(issues)} incohérence(s) détectée(s)")
        print(f"   - {len(migration_steps)} étape(s) de migration")
        
        # Estimation temps
        estimated_time = 2 + (total_user_budgets / 100) + (total_demandes / 1000)
        print(f"⏱️ Temps estimé: {estimated_time:.1f}h")
        
        print(f"\n✅ Audit terminé - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur audit: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = audit_current_state()
    print(f"\n{'='*60}")
    if success:
        print("🎉 Audit terminé avec succès!")
        print("Prochaine étape: python migration_by_only/02_backup_database.py")
    else:
        print("💥 Audit échoué!")
    
    exit(0 if success else 1)
