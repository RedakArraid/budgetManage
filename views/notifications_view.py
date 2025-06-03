"""
Vue pour les notifications
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from controllers.auth_controller import AuthController

@AuthController.require_auth
def notifications_page():
    """Page des notifications"""
    try:
        from views.components.header import display_header
        display_header()
    except ImportError:
        st.subheader("🔔 Notifications")
    
    user_id = AuthController.get_current_user_id()
    
    # Récupérer les notifications
    try:
        notifications = _get_user_notifications(user_id)
    except Exception as e:
        st.error(f"Erreur lors du chargement des notifications: {e}")
        notifications = pd.DataFrame()
    
    if notifications.empty:
        st.info("📭 Aucune notification")
        return
    
    # Actions sur les notifications
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Marquer tout comme lu", use_container_width=True):
            _mark_all_as_read(user_id)
            st.success("✅ Notifications marquées comme lues")
            st.rerun()
    
    with col2:
        if st.button("🗑️ Supprimer tout", use_container_width=True):
            _delete_all_notifications(user_id)
            st.success("✅ Notifications supprimées")
            st.rerun()
    
    st.markdown("---")
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox(
            "Statut",
            ['Toutes', 'Non lues', 'Lues'],
            key='notif_status_filter'
        )
    
    with col2:
        filter_type = st.selectbox(
            "Type",
            ['Tous'] + list(notifications['type_notification'].unique()) if not notifications.empty else ['Tous'],
            key='notif_type_filter'
        )
    
    # Filtrer les notifications
    filtered_notifications = _filter_notifications(notifications, filter_status, filter_type)
    
    # Afficher les notifications
    _display_notifications(filtered_notifications, user_id)

def _get_user_notifications(user_id, limit=50):
    """Récupère les notifications de l'utilisateur"""
    try:
        # Simulation des notifications si le service n'est pas disponible
        from models.notification import NotificationModel
        return NotificationModel.get_user_notifications(user_id, limit)
    except ImportError:
        # Fallback avec des données simulées
        return _get_simulated_notifications(user_id)

def _get_simulated_notifications(user_id):
    """Génère des notifications simulées pour les tests"""
    notifications_data = [
        {
            'id': 1,
            'titre': 'Demande validée',
            'message': 'Votre demande "Salon Marketing 2024" a été validée par le DR.',
            'type_notification': 'demande_validee',
            'is_read': False,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'nom_manifestation': 'Salon Marketing 2024'
        },
        {
            'id': 2,
            'titre': 'Nouvelle demande à valider',
            'message': 'Une nouvelle demande attend votre validation.',
            'type_notification': 'demande_validation',
            'is_read': True,
            'created_at': (datetime.now() - pd.Timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'nom_manifestation': 'Conférence Tech'
        },
        {
            'id': 3,
            'titre': 'Assignation au DR',
            'message': 'Vous avez été assigné au Directeur Régional Nord.',
            'type_notification': 'assignation_dr',
            'is_read': False,
            'created_at': (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'nom_manifestation': None
        }
    ]
    
    return pd.DataFrame(notifications_data)

def _filter_notifications(notifications, status_filter, type_filter):
    """Filtre les notifications selon les critères"""
    filtered = notifications.copy()
    
    if status_filter == 'Non lues':
        filtered = filtered[filtered['is_read'] == False]
    elif status_filter == 'Lues':
        filtered = filtered[filtered['is_read'] == True]
    
    if type_filter != 'Tous':
        filtered = filtered[filtered['type_notification'] == type_filter]
    
    return filtered

def _display_notifications(notifications, user_id):
    """Affiche la liste des notifications"""
    if notifications.empty:
        st.info("Aucune notification correspondant aux filtres")
        return
    
    st.markdown(f"**{len(notifications)} notification(s)**")
    
    for idx, notif in notifications.iterrows():
        _display_notification_card(notif, user_id)

def _display_notification_card(notif, user_id):
    """Affiche une carte de notification"""
    # Déterminer l'icône et la couleur selon le type
    type_icons = {
        'demande_validee': '✅',
        'demande_rejetee': '❌',
        'demande_validation': '⏳',
        'assignation_dr': '👥',
        'rappel_validation': '⚡',
        'nouveau_tc_assigne': '👤'
    }
    
    icon = type_icons.get(notif['type_notification'], '📬')
    read_status = "✅" if notif['is_read'] else "🔴"
    
    # Classe CSS selon le statut
    card_class = "notification-card" if notif['is_read'] else "notification-unread"
    
    with st.container():
        st.markdown(f"""
        <div class="{card_class}" style="
            background: {'#1a1a2e' if notif['is_read'] else '#2d1b2e'};
            border: 1px solid {'#16213e' if notif['is_read'] else '#ff6b6b'};
            border-left: 4px solid {'#4CAF50' if notif['is_read'] else '#ff6b6b'};
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
        ">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <h4 style="margin: 0 0 0.5rem 0; color: #4CAF50;">
                        {read_status} {icon} {notif['titre']}
                    </h4>
                    <p style="margin: 0; color: #ccc;">{notif['message']}</p>
                    {f"<p style='margin: 0.5rem 0 0 0; color: #888; font-size: 0.8rem;'>📋 Demande: {notif['nom_manifestation']}</p>" if notif.get('nom_manifestation') else ""}
                </div>
                <div style="text-align: right;">
                    <small style="color: #888;">{notif['created_at'][:16]}</small>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Actions sur la notification
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if not notif['is_read']:
                if st.button("👁️ Marquer comme lu", key=f"read_{notif['id']}", use_container_width=True):
                    _mark_notification_as_read(notif['id'])
                    st.rerun()
        
        with col2:
            if notif.get('nom_manifestation'):
                if st.button("📋 Voir demande", key=f"view_{notif['id']}", use_container_width=True):
                    st.session_state.page = "demandes"
                    st.rerun()
        
        with col3:
            if st.button("🗑️ Supprimer", key=f"delete_{notif['id']}", use_container_width=True):
                _delete_notification(notif['id'])
                st.rerun()

def _mark_all_as_read(user_id):
    """Marque toutes les notifications comme lues"""
    try:
        from models.notification import NotificationModel
        NotificationModel.mark_all_as_read(user_id)
    except ImportError:
        # Simulation pour les tests
        pass

def _delete_all_notifications(user_id):
    """Supprime toutes les notifications"""
    try:
        from models.notification import NotificationModel
        NotificationModel.delete_all_user_notifications(user_id)
    except ImportError:
        # Simulation pour les tests
        pass

def _mark_notification_as_read(notification_id):
    """Marque une notification comme lue"""
    try:
        from models.notification import NotificationModel
        NotificationModel.mark_as_read(notification_id)
    except ImportError:
        # Simulation pour les tests
        pass

def _delete_notification(notification_id):
    """Supprime une notification"""
    try:
        from models.notification import NotificationModel
        NotificationModel.delete_notification(notification_id)
    except ImportError:
        # Simulation pour les tests
        pass
