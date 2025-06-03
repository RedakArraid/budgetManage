"""
SharePoint synchronization service
"""
import threading
import time
import streamlit as st
import os
from datetime import datetime, timedelta
from typing import Dict, Any

class SharePointSyncService:
    """Service de synchronisation automatique SharePoint"""
    
    def __init__(self, database):
        self.database = database
        self.running = False
        self.sync_thread = None
        self._status = {
            'last_sync': None,
            'sync_count': 0,
            'error_count': 0,
            'last_error': None
        }
    
    def start_auto_sync(self, interval: int = 30):
        """Démarrer la synchronisation automatique"""
        if self.running:
            return
        
        self.running = True
        self.sync_thread = threading.Thread(
            target=self._sync_loop, 
            args=(interval,),
            daemon=True
        )
        self.sync_thread.start()
        print(f"🔄 Synchronisation automatique démarrée (intervalle: {interval}s)")
    
    def stop_auto_sync(self):
        """Arrêter la synchronisation automatique"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        print("⏹️ Synchronisation automatique arrêtée")
    
    def _sync_loop(self, interval: int):
        """Boucle de synchronisation en arrière-plan"""
        while self.running:
            try:
                # Vérifier si SharePoint a une version plus récente
                if self._should_sync():
                    self._perform_background_sync()
                
                self._status['last_sync'] = datetime.now()
                
            except Exception as e:
                self._status['error_count'] += 1
                self._status['last_error'] = str(e)
                print(f"⚠️ Erreur sync automatique: {e}")
            
            # Attendre avant la prochaine vérification
            for _ in range(interval):
                if not self.running:
                    break
                time.sleep(1)
    
    def _should_sync(self) -> bool:
        """Déterminer si une synchronisation est nécessaire"""
        try:
            if not self.database.is_sharepoint_available():
                return False
            
            sharepoint_db = self.database.config.database_path
            local_db = self.database.local_db
            
            # Synchroniser si SharePoint est plus récent
            if os.path.exists(sharepoint_db) and os.path.exists(local_db):
                sharepoint_mtime = os.path.getmtime(sharepoint_db)
                local_mtime = os.path.getmtime(local_db)
                
                return sharepoint_mtime > local_mtime + 5  # 5 secondes de tolérance
            
            return True
            
        except Exception:
            return False
    
    def _perform_background_sync(self):
        """Effectuer synchronisation en arrière-plan"""
        try:
            # Ne pas utiliser le verrou pour la sync en lecture seule
            if self._is_safe_to_sync():
                self.database._sync_from_sharepoint()
                self._status['sync_count'] += 1
                
                # Notifier Streamlit si possible
                try:
                    if hasattr(st, 'session_state'):
                        st.session_state.last_sharepoint_sync = datetime.now()
                except:
                    pass
                
        except Exception as e:
            raise e
    
    def _is_safe_to_sync(self) -> bool:
        """Vérifier si il est sûr de synchroniser"""
        # Ne pas synchroniser si un verrou existe récemment
        lock_file = self.database.config.lock_file
        if os.path.exists(lock_file):
            lock_age = time.time() - os.path.getmtime(lock_file)
            return lock_age > 30  # Attendre 30 secondes après un verrou
        
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Obtenir le statut du service de synchronisation"""
        status = self._status.copy()
        status.update({
            'running': self.running,
            'sharepoint_available': self.database.is_sharepoint_available(),
            'database_status': self.database.get_sync_status()
        })
        return status
    
    def force_sync(self) -> bool:
        """Forcer une synchronisation immédiate"""
        try:
            if self.database.is_sharepoint_available():
                self.database.force_sync_from_sharepoint()
                self._status['sync_count'] += 1
                self._status['last_sync'] = datetime.now()
                return True
            return False
        except Exception as e:
            self._status['error_count'] += 1
            self._status['last_error'] = str(e)
            return False

# Instance globale du service
sync_service = None

def get_sync_service(database=None):
    """Obtenir l'instance du service de synchronisation"""
    global sync_service
    if sync_service is None and database:
        sync_service = SharePointSyncService(database)
    return sync_service
