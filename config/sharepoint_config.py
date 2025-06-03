"""
SharePoint configuration for BudgetManage
"""
import os
import shutil
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass
from contextlib import contextmanager

@dataclass
class SharePointConfig:
    """Configuration SharePoint"""
    # Chemin SharePoint (monté comme lecteur réseau ou sync OneDrive)
    sharepoint_drive: str = os.getenv("SHAREPOINT_DRIVE", "S:")
    sharepoint_folder: str = os.getenv("SHAREPOINT_FOLDER", "BudgetManage-Shared")
    
    # Chemins complets
    @property
    def base_path(self) -> str:
        return os.path.join(self.sharepoint_drive, self.sharepoint_folder)
    
    @property
    def database_path(self) -> str:
        return os.path.join(self.base_path, "budget_workflow.db")
    
    @property
    def backup_folder(self) -> str:
        return os.path.join(self.base_path, "backups")
    
    @property
    def logs_folder(self) -> str:
        return os.path.join(self.base_path, "logs")
    
    @property
    def lock_file(self) -> str:
        return os.path.join(self.base_path, "db.lock")
    
    # Configuration de synchronisation
    sync_interval: int = int(os.getenv("SYNC_INTERVAL", "30"))  # secondes
    enable_auto_backup: bool = os.getenv("AUTO_BACKUP", "true").lower() == "true"
    backup_frequency: int = int(os.getenv("BACKUP_FREQUENCY", "3600"))  # 1 heure
    lock_timeout: int = 60  # timeout pour le verrou en secondes
    
    def __post_init__(self):
        """Créer les dossiers nécessaires"""
        try:
            os.makedirs(self.base_path, exist_ok=True)
            os.makedirs(self.backup_folder, exist_ok=True)
            os.makedirs(self.logs_folder, exist_ok=True)
        except Exception as e:
            print(f"⚠️ Impossible de créer les dossiers SharePoint: {e}")

class SharePointDatabase:
    """Gestionnaire base SQLite sur SharePoint avec gestion des conflits"""
    
    def __init__(self):
        self.config = SharePointConfig()
        self.local_db = "budget_workflow_local.db"
        self._last_sync = datetime.now()
        self._sync_lock = threading.Lock()
    
    def is_sharepoint_available(self) -> bool:
        """Toujours retourner False pour forcer le mode local"""
        return False
        
    @contextmanager
    def get_connection(self):
        """Connexion avec gestion des conflits et synchronisation"""
        import sqlite3
        
        # 1. Synchroniser depuis SharePoint
        self._sync_from_sharepoint()
        
        # 2. Acquérir verrou pour les modifications
        with self._acquire_lock():
            conn = sqlite3.connect(self.local_db)
            conn.row_factory = sqlite3.Row
            
            # Configuration SQLite pour accès concurrent
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            
            try:
                yield conn
                conn.commit()
                # 3. Synchroniser vers SharePoint après modification
                self._sync_to_sharepoint()
            except Exception as e:
                conn.rollback()
                raise e
            finally:
                conn.close()
    
    def _sync_from_sharepoint(self):
        """Récupérer la dernière version depuis SharePoint"""
        with self._sync_lock:
            try:
                sharepoint_db = self.config.database_path
                
                if not os.path.exists(sharepoint_db):
                    # Première fois : créer la base sur SharePoint
                    if os.path.exists(self.local_db):
                        shutil.copy2(self.local_db, sharepoint_db)
                        print(f"✅ Base initiale créée sur SharePoint")
                    return
                
                # Vérifier si SharePoint a une version plus récente
                if not os.path.exists(self.local_db) or \
                   os.path.getmtime(sharepoint_db) > os.path.getmtime(self.local_db):
                    
                    # Créer backup de la version locale si elle existe
                    if os.path.exists(self.local_db):
                        backup_name = f"local_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
                        shutil.copy2(self.local_db, backup_name)
                    
                    # Copier depuis SharePoint
                    shutil.copy2(sharepoint_db, self.local_db)
                    self._last_sync = datetime.now()
                    print(f"🔄 Base synchronisée depuis SharePoint")
                    
            except Exception as e:
                print(f"⚠️ Erreur synchronisation depuis SharePoint: {e}")
                # En cas d'erreur, utiliser la version locale
                if not os.path.exists(self.local_db):
                    self._create_empty_database()
    
    def _sync_to_sharepoint(self):
        """Envoyer les modifications vers SharePoint"""
        with self._sync_lock:
            try:
                sharepoint_db = self.config.database_path
                
                # Créer backup avant écrasement
                if os.path.exists(sharepoint_db) and self.config.enable_auto_backup:
                    self._create_backup(sharepoint_db)
                
                # Copier la version locale vers SharePoint
                shutil.copy2(self.local_db, sharepoint_db)
                self._last_sync = datetime.now()
                print(f"📤 Base synchronisée vers SharePoint")
                
                # Log de synchronisation
                self._log_sync_activity("sync_to_sharepoint")
                
            except Exception as e:
                print(f"⚠️ Erreur synchronisation vers SharePoint: {e}")
                # Log de l'erreur
                self._log_sync_activity("sync_error", str(e))
    
    def _create_backup(self, source_db):
        """Créer une sauvegarde"""
        try:
            backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            backup_path = os.path.join(self.config.backup_folder, backup_name)
            shutil.copy2(source_db, backup_path)
            
            # Nettoyer les anciennes sauvegardes (garder 10 dernières)
            self._cleanup_old_backups()
            
        except Exception as e:
            print(f"⚠️ Erreur création backup: {e}")
    
    def _cleanup_old_backups(self, keep_count=10):
        """Nettoyer les anciennes sauvegardes"""
        try:
            backup_files = []
            for file in os.listdir(self.config.backup_folder):
                if file.startswith("backup_") and file.endswith(".db"):
                    file_path = os.path.join(self.config.backup_folder, file)
                    backup_files.append((file_path, os.path.getmtime(file_path)))
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: x[1], reverse=True)
            
            # Supprimer les anciens
            for file_path, _ in backup_files[keep_count:]:
                os.remove(file_path)
                
        except Exception as e:
            print(f"⚠️ Erreur nettoyage backups: {e}")
    
    @contextmanager
    def _acquire_lock(self):
        """Système de verrou pour éviter les conflits d'écriture"""
        lock_file = self.config.lock_file
        start_time = time.time()
        lock_acquired = False
        
        try:
            # Attendre que le verrou soit libre
            while os.path.exists(lock_file):
                if time.time() - start_time > self.config.lock_timeout:
                    # Vérifier si le verrou est ancien (processus mort)
                    if os.path.getmtime(lock_file) < time.time() - 300:  # 5 minutes
                        os.remove(lock_file)
                        print("🔓 Verrou ancien supprimé")
                        break
                    else:
                        raise TimeoutError("Impossible d'acquérir le verrou de base de données")
                time.sleep(0.5)
            
            # Créer le verrou
            lock_info = {
                'pid': os.getpid(),
                'timestamp': datetime.now().isoformat(),
                'user': os.getenv('USERNAME', 'unknown')
            }
            
            with open(lock_file, 'w') as f:
                import json
                json.dump(lock_info, f)
            
            lock_acquired = True
            yield
            
        finally:
            # Libérer le verrou
            if lock_acquired and os.path.exists(lock_file):
                try:
                    os.remove(lock_file)
                except Exception:
                    pass  # Ignorer les erreurs de suppression
    
    def _create_empty_database(self):
        """Créer une base de données vide"""
        import sqlite3
        from models.database import Database
        
        # Utiliser la méthode d'initialisation existante
        db = Database()
        db.db_path = self.local_db
        db.init_database()
        print(f"📄 Base de données locale créée")
    
    def _log_sync_activity(self, action, details=""):
        """Logger les activités de synchronisation"""
        try:
            log_file = os.path.join(self.config.logs_folder, f"sync_{datetime.now().strftime('%Y%m')}.log")
            log_entry = f"{datetime.now().isoformat()} - {action} - {details}\n"
            
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
        except Exception:
            pass  # Ignorer les erreurs de log
    
    def is_sharepoint_available_original(self) -> bool:
        """Vérifier si SharePoint est disponible (version originale désactivée)"""
        try:
            return os.path.exists(self.config.base_path) and os.access(self.config.base_path, os.W_OK)
        except Exception:
            return False
    
    def get_sync_status(self) -> dict:
        """Obtenir le statut de synchronisation"""
        return {
            'last_sync': self._last_sync,
            'sharepoint_available': self.is_sharepoint_available(),
            'local_db_exists': os.path.exists(self.local_db),
            'sharepoint_db_exists': os.path.exists(self.config.database_path),
            'lock_exists': os.path.exists(self.config.lock_file)
        }
    
    def force_sync_from_sharepoint(self):
        """Forcer la synchronisation depuis SharePoint"""
        if os.path.exists(self.local_db):
            backup_name = f"force_sync_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            shutil.copy2(self.local_db, backup_name)
        
        self._sync_from_sharepoint()
        return True
    
    def get_active_users(self) -> list:
        """Obtenir la liste des utilisateurs actifs (basé sur les verrous récents)"""
        try:
            active_users = []
            
            # Vérifier le verrou actuel
            if os.path.exists(self.config.lock_file):
                with open(self.config.lock_file, 'r') as f:
                    import json
                    lock_info = json.load(f)
                    active_users.append({
                        'user': lock_info.get('user', 'unknown'),
                        'timestamp': lock_info.get('timestamp'),
                        'status': 'active'
                    })
            
            # Analyser les logs récents
            current_month = datetime.now().strftime('%Y%m')
            log_file = os.path.join(self.config.logs_folder, f"sync_{current_month}.log")
            
            if os.path.exists(log_file):
                recent_cutoff = datetime.now() - timedelta(minutes=10)
                with open(log_file, 'r') as f:
                    for line in f.readlines()[-50:]:  # 50 dernières lignes
                        try:
                            timestamp_str = line.split(' - ')[0]
                            timestamp = datetime.fromisoformat(timestamp_str)
                            if timestamp > recent_cutoff:
                                # Extraire info utilisateur si disponible
                                pass
                        except Exception:
                            continue
            
            return active_users
            
        except Exception as e:
            print(f"⚠️ Erreur récupération utilisateurs actifs: {e}")
            return []

# Instance globale
sharepoint_db = SharePointDatabase()
