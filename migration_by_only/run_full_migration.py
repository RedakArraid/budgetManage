#!/usr/bin/env python3
"""
Script principal de migration complète vers BY uniquement
Lance automatiquement toutes les étapes de migration
"""
import sys
import os
import subprocess
from datetime import datetime

def run_script(script_path: str) -> bool:
    """Exécuter un script et retourner le résultat"""
    try:
        print(f"\n🚀 Exécution: {os.path.basename(script_path)}")
        print("-" * 50)
        
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=False, 
                              text=True, 
                              cwd=os.path.dirname(script_path))
        
        if result.returncode == 0:
            print(f"✅ {os.path.basename(script_path)} - SUCCÈS")
            return True
        else:
            print(f"❌ {os.path.basename(script_path)} - ÉCHEC (code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"💥 Erreur exécution {script_path}: {e}")
        return False

def main():
    """Migration complète automatique"""
    print("🔄 MIGRATION COMPLÈTE VERS BY UNIQUEMENT")
    print("=" * 60)
    print(f"Début: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Chemin du dossier migration
    migration_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Scripts à exécuter dans l'ordre
    scripts = [
        "01_audit_current_state.py",
        "02_backup_database.py",
        "03_migrate_user_budgets.py",
        "04_update_user_budget_model.py",
        "05_clean_demande_model.py",
        "06_clean_database_init.py"
    ]
    
    print("📋 ÉTAPES DE MIGRATION:")
    for i, script in enumerate(scripts, 1):
        description = {
            "01_audit_current_state.py": "Audit état initial",
            "02_backup_database.py": "Backup base de données",
            "03_migrate_user_budgets.py": "Migration user_budgets",
            "04_update_user_budget_model.py": "Mise à jour UserBudgetModel",
            "05_clean_demande_model.py": "Nettoyage DemandeModel",
            "06_clean_database_init.py": "Nettoyage database.py"
        }
        print(f"  {i}. {description.get(script, script)}")
    
    print(f"\n{'='*60}")
    
    # Demander confirmation
    response = input("🤔 Continuer la migration automatique ? [y/N]: ")
    if response.lower() not in ['y', 'yes', 'o', 'oui']:
        print("❌ Migration annulée par l'utilisateur")
        return False
    
    print("\n🚀 DÉBUT MIGRATION AUTOMATIQUE")
    print("=" * 40)
    
    # Exécuter chaque script
    for i, script in enumerate(scripts, 1):
        script_path = os.path.join(migration_dir, script)
        
        if not os.path.exists(script_path):
            print(f"❌ Script introuvable: {script}")
            return False
        
        print(f"\n📌 ÉTAPE {i}/{len(scripts)}: {script}")
        
        success = run_script(script_path)
        
        if not success:
            print(f"\n💥 ARRÊT À L'ÉTAPE {i}")
            print(f"Script échoué: {script}")
            print("🔧 Actions possibles:")
            print("  1. Corriger le problème et relancer ce script")
            print("  2. Exécuter manuellement les scripts restants")
            print("  3. Restaurer backup et recommencer")
            return False
        
        # Petite pause entre étapes
        if i < len(scripts):
            print(f"\n⏳ Transition vers étape {i+1}...")
            import time
            time.sleep(1)
    
    # Résumé final
    print(f"\n{'='*60}")
    print("🎉 MIGRATION COMPLÈTE RÉUSSIE!")
    print(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("✅ TOUTES LES ÉTAPES TERMINÉES:")
    for i, script in enumerate(scripts, 1):
        description = {
            "01_audit_current_state.py": "Audit état initial",
            "02_backup_database.py": "Backup base de données",
            "03_migrate_user_budgets.py": "Migration user_budgets",
            "04_update_user_budget_model.py": "Mise à jour UserBudgetModel",
            "05_clean_demande_model.py": "Nettoyage DemandeModel",
            "06_clean_database_init.py": "Nettoyage database.py"
        }
        print(f"  ✅ {i}. {description.get(script, script)}")
    
    print(f"\n🆕 NOUVELLES FONCTIONNALITÉS DISPONIBLES:")
    print("  - UserBudgetModel.get_unified_budget_dashboard()")
    print("  - UserBudgetModel.get_budget_alerts()")
    print("  - UserBudgetModel.get_all_fiscal_years()")
    print("  - Corrélation parfaite budget ↔ demandes par année BY")
    
    print(f"\n📋 CHANGEMENTS APPLIQUÉS:")
    print("  - user_budgets utilise 'by' (string) au lieu de fiscal_year (int)")
    print("  - DemandeModel nettoyé (suppression vestiges fiscal_year)")
    print("  - calculate_cy_by() simplifié (2 valeurs au lieu de 3)")
    print("  - database.py ne crée plus de colonne fiscal_year")
    
    print(f"\n🎯 PROCHAINES ÉTAPES OPTIONNELLES:")
    print("  - Tester les nouvelles fonctionnalités dans l'interface")
    print("  - Mettre à jour gestion_budgets_view.py pour utiliser les nouvelles méthodes")
    print("  - Créer des tests de non-régression")
    print("  - Supprimer définitivement la colonne fiscal_year (si souhaitée)")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n⚠️ Migration interrompue par l'utilisateur")
        print("🔧 Pour reprendre, relancez ce script ou exécutez manuellement les étapes restantes")
        exit(130)
    except Exception as e:
        print(f"\n💥 Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
