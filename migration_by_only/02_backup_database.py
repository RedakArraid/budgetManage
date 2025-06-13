#!/usr/bin/env python3
"""
Script de backup de la base de données avant migration
Sauvegarde complète avec timestamp
"""
import sys
import os
import shutil
from datetime import datetime

# Ajouter le répertoire du projet au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def backup_database():
    """Backup complet de la base de données"""
    print("💾 BACKUP - Sauvegarde base de données")
    print("=" * 40)
    
    try:
        from config.settings import db_config
        
        # Chemin base de données source
        source_db = db_config.path
        
        if not os.path.exists(source_db):
            print(f"❌ Base de données source introuvable: {source_db}")
            return False
        
        # Créer dossier de backup
        backup_dir = os.path.join(os.path.dirname(source_db), "backups")
        os.makedirs(backup_dir, exist_ok=True)
        
        # Nom du backup avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"budget_workflow_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copier la base
        print(f"📂 Source: {source_db}")
        print(f"📂 Backup: {backup_path}")
        
        file_size = os.path.getsize(source_db)
        print(f"📊 Taille: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        shutil.copy2(source_db, backup_path)
        
        # Vérifier le backup
        if os.path.exists(backup_path):
            backup_size = os.path.getsize(backup_path)
            if backup_size == file_size:
                print("✅ Backup créé avec succès")
                print(f"✅ Taille vérifiée: {backup_size:,} bytes")
                
                # Créer aussi un backup "latest"
                latest_backup = os.path.join(backup_dir, "budget_workflow_latest.db")
                shutil.copy2(backup_path, latest_backup)
                print(f"✅ Backup latest créé: {latest_backup}")
                
                # Instructions de restauration
                print(f"\n📋 INSTRUCTIONS DE RESTAURATION:")
                print(f"En cas de problème, restaurer avec:")
                print(f"cp {backup_path} {source_db}")
                print(f"ou")
                print(f"cp {latest_backup} {source_db}")
                
                return True
            else:
                print(f"❌ Erreur: Taille différente (source: {file_size}, backup: {backup_size})")
                return False
        else:
            print("❌ Erreur: Backup non créé")
            return False
        
    except Exception as e:
        print(f"❌ Erreur backup: {e}")
        import traceback
        traceback.print_exc()
        return False

def list_existing_backups():
    """Lister les backups existants"""
    try:
        from config.settings import db_config
        
        backup_dir = os.path.join(os.path.dirname(db_config.path), "backups")
        
        if not os.path.exists(backup_dir):
            print("📂 Aucun dossier de backup existant")
            return
        
        backups = [f for f in os.listdir(backup_dir) if f.endswith('.db')]
        
        if not backups:
            print("📂 Aucun backup existant")
            return
        
        print(f"\n📂 BACKUPS EXISTANTS ({len(backups)}):")
        print("-" * 30)
        
        for backup in sorted(backups):
            backup_path = os.path.join(backup_dir, backup)
            size = os.path.getsize(backup_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(backup_path))
            print(f"📄 {backup}")
            print(f"   Taille: {size:,} bytes ({size/1024:.1f} KB)")
            print(f"   Date: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            print()
    
    except Exception as e:
        print(f"⚠️ Erreur listage backups: {e}")

if __name__ == "__main__":
    print("💾 BACKUP MANAGEMENT")
    print("=" * 40)
    
    # Lister backups existants
    list_existing_backups()
    
    # Créer nouveau backup
    success = backup_database()
    
    print(f"\n{'='*40}")
    if success:
        print("🎉 Backup terminé avec succès!")
        print("Prochaine étape: python migration_by_only/03_migrate_user_budgets.py")
    else:
        print("💥 Backup échoué!")
        print("❌ ARRÊT - Ne pas continuer la migration sans backup valide")
    
    exit(0 if success else 1)
