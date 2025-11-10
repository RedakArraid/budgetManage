"""
SharePoint status component for Streamlit interface
"""
import streamlit as st
import os
from datetime import datetime, timedelta
from config.sharepoint_config import sharepoint_db
from services.sharepoint_sync_service import get_sync_service

def display_sharepoint_status():
    """Afficher le statut de connexion SharePoint dans l'interface"""
    
    # Initialiser le service de sync si nécessaire
    sync_service = get_sync_service(sharepoint_db)
    if sync_service and not sync_service.running:
        sync_service.start_auto_sync(interval=30)
    
    # Obtenir le statut
    db_status = sharepoint_db.get_sync_status()
    sync_status = sync_service.get_status() if sync_service else {}
    
    # Affichage en colonnes
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Statut SharePoint
        if db_status['sharepoint_available']:
            st.success("🟢 SharePoint")
            if db_status['sharepoint_db_exists']:
                last_modified = os.path.getmtime(sharepoint_db.config.database_path)
                last_sync_str = datetime.fromtimestamp(last_modified).strftime('%H:%M:%S')
                st.caption(f"Modifiée: {last_sync_str}")
            else:
                st.caption("Base manquante")
        else:
            st.error("🔴 SharePoint")
            st.caption("Indisponible")
    
    with col2:
        # Statut synchronisation
        if sync_status.get('running'):
            st.info("🔄 Sync Auto")
            if sync_status.get('last_sync'):
                last_sync = sync_status['last_sync'].strftime('%H:%M:%S')
                st.caption(f"Dernière: {last_sync}")
        else:
            st.warning("⏸️ Sync OFF")
            st.caption("Non démarrée")
    
    with col3:
        # Actions manuelles
        if st.button("🔄 Sync Manuelle", use_container_width=True):
            if sync_service:
                with st.spinner("Synchronisation..."):
                    success = sync_service.force_sync()
                    if success:
                        st.success("✅ Synchronisé!")
                        st.rerun()
                    else:
                        st.error("❌ Échec sync")
            else:
                st.error("Service non disponible")
    
    with col4:
        # Utilisateurs actifs
        try:
            active_users = sharepoint_db.get_active_users()
            user_count = len(active_users)
            
            if user_count > 0:
                st.metric("👥 Actifs", user_count)
                if user_count > 1:
                    st.caption("⚠️ Accès concurrent")
            else:
                st.metric("👤 Seul", "1")
                st.caption("Accès exclusif")
        except:
            st.metric("👥 Users", "?")
            st.caption("Inconnu")

def get_sharepoint_status_for_sidebar():
    """Obtenir un résumé de statut pour la sidebar"""
    try:
        db_status = sharepoint_db.get_sync_status()
        if db_status['sharepoint_available']:
            if db_status['lock_exists']:
                return "🔒 Verrouillé"
            else:
                return "🟢 Connecté"
        else:
            return "🔴 Hors ligne"
    except:
        return "❓ Inconnu"
