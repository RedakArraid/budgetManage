"""
Composant header réutilisable
"""
import streamlit as st
from controllers.auth_controller import AuthController
from config.settings import get_role_label

def display_header():
    """Afficher l'en-tête de page"""
    if not AuthController.check_session():
        return
    
    user_info = AuthController.get_current_user()
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
