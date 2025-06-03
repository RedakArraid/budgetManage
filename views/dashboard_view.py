"""
Dashboard page view
"""
import streamlit as st
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from config.settings import get_role_label
from utils.date_utils import format_date

@AuthController.require_auth
def dashboard_page():
    """Display dashboard page"""
    user_info = AuthController.get_current_user()
    user_id = AuthController.get_current_user_id()
    role = user_info['role']
    
    # Display header
    _display_header(user_info)
    
    # Get dashboard statistics
    stats = DemandeController.get_dashboard_stats(user_id, role)
    
    st.subheader(f"📊 Tableau de Bord - {user_info['prenom']} {user_info['nom']}")
    
    # Display metrics based on role
    _display_metrics(role, stats)
    
    # Quick actions
    st.markdown("---")
    st.subheader("⚡ Actions Rapides")
    _display_quick_actions(role)
    
    # Recent demandes
    st.markdown("---")
    st.subheader("📋 Demandes Récentes")
    _display_recent_demandes(user_id, role)

def _display_header(user_info):
    """Display page header"""
    role_label = get_role_label(user_info['role'])
    
    st.markdown(f"""
    <div class="header-container">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; color: #4CAF50;">💰 Système de Gestion Budget</h2>
                <p style="margin: 0; color: #888;">
                    Bonjour {user_info['prenom']} {user_info['nom']} 
                    <span class="role-{user_info['role']}">{role_label}</span>
                </p>
            </div>
            <div style="text-align: right;">
                <p style="margin: 0; color: #888; font-size: 0.9rem;">
                    Région: {user_info.get('region', 'N/A')}
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def _display_metrics(role, stats):
    """Display metrics based on user role"""
    if role == 'admin':
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4CAF50; margin: 0;">{stats.get('total_demandes', 0)}</h3>
                <p style="margin: 0; color: #888;">Total Demandes</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #ffc107; margin: 0;">{stats.get('en_attente_dr', 0)}</h3>
                <p style="margin: 0; color: #888;">Attente DR</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #fd7e14; margin: 0;">{stats.get('en_attente_financier', 0)}</h3>
                <p style="margin: 0; color: #888;">Attente Financier</p>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">{stats.get('validees', 0)}</h3>
                <p style="margin: 0; color: #888;">Validées</p>
            </div>
            """, unsafe_allow_html=True)
        with col5:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4CAF50; margin: 0;">{stats.get('montant_valide', 0):,.0f}€</h3>
                <p style="margin: 0; color: #888;">Montant Validé</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif role == 'tc':
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #74b9ff; margin: 0;">{stats.get('mes_demandes', 0)}</h3>
                <p style="margin: 0; color: #888;">Mes Demandes</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">{stats.get('validees', 0)}</h3>
                <p style="margin: 0; color: #888;">Validées</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4CAF50; margin: 0;">{stats.get('montant_valide', 0):,.0f}€</h3>
                <p style="margin: 0; color: #888;">Montant Validé</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif role == 'dr':
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #fdcb6e; margin: 0;">{stats.get('total_demandes', 0)}</h3>
                <p style="margin: 0; color: #888;">Total Demandes</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #ffc107; margin: 0;">{stats.get('en_attente_validation', 0)}</h3>
                <p style="margin: 0; color: #888;">En Attente Validation</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif role in ['dr_financier', 'dg']:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #fd7e14; margin: 0;">{stats.get('en_attente_validation', 0)}</h3>
                <p style="margin: 0; color: #888;">En Attente Validation</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #28a745; margin: 0;">{stats.get('validees', 0)}</h3>
                <p style="margin: 0; color: #888;">Validées</p>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #4CAF50; margin: 0;">{stats.get('montant_valide', 0):,.0f}€</h3>
                <p style="margin: 0; color: #888;">Montant Validé</p>
            </div>
            """, unsafe_allow_html=True)

# Fonctions utilitaires pour les actions rapides (pour assurer le déclenchement)
def go_to_nouvelle_demande():
    print("[DEBUG] Quick action button clicked: Nouvelle Demande")
    st.session_state.page = "nouvelle_demande"
    st.rerun()

def go_to_gestion_utilisateurs():
    print("[DEBUG] Quick action button clicked: Gestion Utilisateurs")
    st.session_state.page = "gestion_utilisateurs"
    st.rerun()

def go_to_mes_demandes():
    print("[DEBUG] Quick action button clicked: Mes Demandes")
    st.session_state.page = "demandes"
    st.rerun()

def go_to_validations():
    print("[DEBUG] Quick action button clicked: Validations")
    st.session_state.page = "validations"
    st.rerun()

def go_to_analytics():
    print("[DEBUG] Quick action button clicked: Analytics")
    st.session_state.page = "analytics"
    st.rerun()

def go_to_notifications():
    print("[DEBUG] Quick action button clicked: Notifications")
    st.session_state.page = "notifications"
    st.rerun()

# Section Actions Rapides
def _display_quick_actions(role):
    # Utiliser des colonnes pour organiser les boutons
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if role in ['tc', 'dr', 'marketing']:
            if st.button("➕ Nouvelle Demande", use_container_width=True, key='quick_action_new_demande'):
                go_to_nouvelle_demande()
        elif role == 'admin':
            if st.button("👥 Gestion Utilisateurs", use_container_width=True, key='quick_action_manage_users'):
                go_to_gestion_utilisateurs()

    with col2:
        if st.button("📋 Mes Demandes", use_container_width=True, key='quick_action_mes_demandes'):
            go_to_mes_demandes()

    with col3:
        if role in ['dr', 'dr_financier', 'dg']:
            if st.button("✅ Validations", use_container_width=True, key='quick_action_validations'):
                go_to_validations()
        else:
            if st.button("📊 Analytics", use_container_width=True, key='quick_action_analytics'):
                go_to_analytics()

    with col4:
        if st.button("🔔 Notifications", use_container_width=True, key='quick_action_notifications'):
            go_to_notifications()


# Section Demandes Récentes (affichée pour tous sauf admin)
def _display_recent_demandes(user_id, role):
    """Display recent demandes"""
    demandes = DemandeController.get_demandes_for_user(user_id, role)
    
    if not demandes.empty:
        # Show only 5 most recent
        recent_demandes = demandes.head(5)
        
        for idx, row in recent_demandes.iterrows():
            _display_demande_card(row)
        
        if len(demandes) > 5:
            if st.button(f"Voir toutes les demandes ({len(demandes)})", use_container_width=True):
                st.session_state.page = "demandes"
                st.rerun()
    else:
        st.info("Aucune demande pour le moment")

def _display_demande_card(row):
    """Display a single demande card"""
    from config.settings import get_status_info
    
    status_info = get_status_info(row['status'])
    status_class = f"status-{row['status']}"
    
    st.markdown(f"""
    <div class="demand-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="flex: 1;">
                <h4 style="margin: 0 0 0.5rem 0; color: #4CAF50;">{row['nom_manifestation']}</h4>
                <p style="margin: 0; color: #888; font-size: 0.9rem;">
                    🏢 {row['client']} • 📅 {format_date(row['date_evenement'])} • 📍 {row['lieu']}
                </p>
                <p style="margin: 0.5rem 0 0 0; color: #aaa; font-size: 0.8rem;">
                    👤 {row['prenom']} {row['nom']} • 📧 {row['email']}
                </p>
                <span class="{status_class}">{status_info['label']}</span>
            </div>
            <div style="text-align: right;">
                <h3 style="margin: 0; color: #4CAF50;">{row['montant']:,.0f}€</h3>
                <p style="margin: 0; color: #888; font-size: 0.8rem;">{row['updated_at'][:10]}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
