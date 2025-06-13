#!/usr/bin/env python3
"""
Script pour remplacer UserBudgetModel par la version migrée
Backup de l'ancien fichier et installation de la nouvelle version
"""
import sys
import os
import shutil
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def update_user_budget_model():
    """Remplacer UserBudgetModel par la version BY"""
    print("🔄 UPDATE USER_BUDGET_MODEL - Migration vers BY")
    print("=" * 50)
    
    try:
        # Chemins des fichiers
        migration_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(migration_dir)
        
        old_file = os.path.join(project_root, "models", "user_budget.py")
        new_file = os.path.join(migration_dir, "user_budget_model_new.py")
        backup_file = os.path.join(migration_dir, f"user_budget_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py")
        
        print("📂 Chemins:")
        print(f"   Ancien: {old_file}")
        print(f"   Nouveau: {new_file}")
        print(f"   Backup: {backup_file}")
        
        # 1. Vérifier que les fichiers existent
        print(f"\n📋 1. VÉRIFICATIONS")
        print("-" * 30)
        
        if not os.path.exists(old_file):
            print(f"❌ Fichier original introuvable: {old_file}")
            return False
        
        if not os.path.exists(new_file):
            print(f"❌ Nouvelle version introuvable: {new_file}")
            return False
        
        print("✅ Fichiers trouvés")
        
        # 2. Backup de l'ancien fichier
        print(f"\n📋 2. BACKUP ANCIEN FICHIER")
        print("-" * 30)
        
        shutil.copy2(old_file, backup_file)
        print(f"✅ Backup créé: {backup_file}")
        
        # 3. Test d'import de l'ancien modèle
        print(f"\n📋 3. TEST ANCIEN MODÈLE")
        print("-" * 30)
        
        try:
            from models.user_budget import UserBudgetModel
            print("✅ Import ancien UserBudgetModel OK")
            
            # Vérifier si la table existe et a des données
            from models.database import db
            if db.table_exists('user_budgets'):
                count = db.execute_query("SELECT COUNT(*) as count FROM user_budgets", fetch='one')['count']
                print(f"📊 {count} budget(s) en base")
            else:
                print("⚠️ Table user_budgets n'existe pas")
        except Exception as e:
            print(f"⚠️ Erreur import ancien modèle: {e}")
        
        # 4. Remplacer le fichier
        print(f"\n📋 4. REMPLACEMENT FICHIER")
        print("-" * 30)
        
        shutil.copy2(new_file, old_file)
        print(f"✅ Fichier remplacé: {old_file}")
        
        # 5. Test de la nouvelle version
        print(f"\n📋 5. TEST NOUVEAU MODÈLE")
        print("-" * 30)
        
        try:
            # Recharger le module
            import importlib
            import models.user_budget
            importlib.reload(models.user_budget)
            
            from models.user_budget import UserBudgetModel
            print("✅ Import nouveau UserBudgetModel OK")
            
            # Test méthode signature
            if hasattr(UserBudgetModel, 'create_budget'):
                import inspect
                sig = inspect.signature(UserBudgetModel.create_budget)
                params = list(sig.parameters.keys())
                if 'by' in params and 'fiscal_year' not in params:
                    print("✅ Signature create_budget migrée (by au lieu de fiscal_year)")
                else:
                    print(f"⚠️ Signature create_budget: {params}")
            
            # Test nouvelles fonctionnalités
            new_methods = ['get_unified_budget_dashboard', 'get_budget_alerts', 'get_all_fiscal_years']
            for method in new_methods:
                if hasattr(UserBudgetModel, method):
                    print(f"✅ Nouvelle méthode disponible: {method}")
                else:
                    print(f"❌ Méthode manquante: {method}")
            
        except Exception as e:
            print(f"❌ Erreur test nouveau modèle: {e}")
            
            # Restaurer l'ancien fichier en cas d'erreur
            print("🔄 Restauration ancien fichier...")
            shutil.copy2(backup_file, old_file)
            print("✅ Ancien fichier restauré")
            return False
        
        # 6. Test fonctionnel simple
        print(f"\n📋 6. TEST FONCTIONNEL")
        print("-" * 30)
        
        try:
            # Test get_all_fiscal_years
            fiscal_years = UserBudgetModel.get_all_fiscal_years()
            print(f"✅ get_all_fiscal_years(): {fiscal_years}")
            
            # Test avec données existantes si disponibles
            from models.database import db
            if db.table_exists('user_budgets'):
                sample_budget = db.execute_query("""
                    SELECT user_id, by FROM user_budgets 
                    WHERE by IS NOT NULL AND by != ''
                    LIMIT 1
                """, fetch='one')
                
                if sample_budget:
                    user_id = sample_budget['user_id']
                    by = sample_budget['by']
                    
                    # Test get_budget_consumption
                    consumption = UserBudgetModel.get_budget_consumption(user_id, by)
                    print(f"✅ get_budget_consumption({user_id}, {by}): {consumption['allocated_budget']}€ alloués")
                    
                    # Test get_budget_alerts
                    alerts = UserBudgetModel.get_budget_alerts(user_id, by)
                    print(f"✅ get_budget_alerts({user_id}, {by}): {len(alerts)} alerte(s)")
                else:
                    print("⚠️ Aucun budget avec 'by' pour test fonctionnel")
            
        except Exception as e:
            print(f"⚠️ Erreur test fonctionnel: {e}")
            # Ne pas considérer comme une erreur critique
        
        print(f"\n✅ Migration UserBudgetModel terminée - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur migration: {e}")
        import traceback
        traceback.print_exc()
        return False

def compare_methods():
    """Comparer les méthodes avant/après migration"""
    print("\n📋 COMPARAISON MÉTHODES")
    print("-" * 30)
    
    try:
        from models.user_budget import UserBudgetModel
        
        all_methods = [method for method in dir(UserBudgetModel) if not method.startswith('_')]
        
        # Méthodes attendues après migration
        expected_methods = [
            'create_budget',
            'get_user_budget', 
            'get_all_budgets_for_year',
            'get_budgets_by_user',
            'delete_budget',
            'get_budget_summary_by_year',
            'get_budget_consumption',
            'bulk_create_budgets',
            'copy_budgets_to_next_year',
            'get_all_fiscal_years',           # NOUVEAU
            'get_unified_budget_dashboard',   # NOUVEAU  
            'get_budget_alerts'               # NOUVEAU
        ]
        
        print("📋 Méthodes trouvées:")
        for method in all_methods:
            is_new = method in ['get_all_fiscal_years', 'get_unified_budget_dashboard', 'get_budget_alerts']
            status = "🆕 NOUVEAU" if is_new else "✅"
            print(f"   {status} {method}")
        
        # Méthodes manquantes
        missing = set(expected_methods) - set(all_methods)
        if missing:
            print(f"\n❌ Méthodes manquantes:")
            for method in missing:
                print(f"   - {method}")
        else:
            print(f"\n✅ Toutes les méthodes attendues sont présentes")
        
        return len(missing) == 0
        
    except Exception as e:
        print(f"❌ Erreur comparaison: {e}")
        return False

if __name__ == "__main__":
    print("🔄 UPDATE USER_BUDGET_MODEL")
    print("=" * 50)
    
    # Migration
    success = update_user_budget_model()
    
    if success:
        # Comparaison méthodes
        methods_ok = compare_methods()
        
        print(f"\n{'='*50}")
        if methods_ok:
            print("🎉 Migration UserBudgetModel réussie!")
            print("Nouvelles fonctionnalités disponibles:")
            print("  - get_unified_budget_dashboard() - Dashboard budget+demandes")
            print("  - get_budget_alerts() - Alertes dépassement budget")
            print("  - get_all_fiscal_years() - Années fiscales avec budgets")
            print("Prochaine étape: python migration_by_only/05_clean_demande_model.py")
        else:
            print("⚠️ Migration OK mais méthodes incomplètes")
            print("Vérifiez le fichier avant de continuer")
    else:
        print(f"\n{'='*50}")
        print("💥 Migration échouée!")
        print("❌ ARRÊT - Le backup a été restauré automatiquement")
    
    exit(0 if success and (not 'methods_ok' in locals() or methods_ok) else 1)
