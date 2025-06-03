"""
Login page view
"""
import streamlit as st
from controllers.auth_controller import AuthController

def login_page():
    """Display login page"""
    st.markdown("""
    <div class="login-container">
        <div class="login-header">
            <h1>💰</h1>
            <h2>Connexion</h2>
            <p>Système de Gestion Budget</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="votre@email.com")
        password = st.text_input("🔒 Mot de passe", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("🚀 Se connecter", use_container_width=True)
        with col2:
            if st.form_submit_button("ℹ️ Aide", use_container_width=True):
                st.info("Contactez l'administrateur pour créer votre compte")
    
    if login_btn:
        if email and password:
            result = AuthController.login(email, password)
            if result:
                st.session_state.logged_in = True
                st.session_state.user_id = result['id']
                st.session_state.user_info = result
                st.session_state.page = "dashboard"
                st.success("✅ Connexion réussie !")
                st.rerun()
        else:
            st.warning("⚠️ Veuillez remplir tous les champs")
