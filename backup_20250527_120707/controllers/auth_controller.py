"""
Authentication controller
"""
import streamlit as st
from typing import Optional, Dict, Any

from models.user import UserModel
from models.activity_log import ActivityLogModel
from utils.validators import validate_email, validate_password

class AuthController:
    """Controller for authentication operations"""
    
    @staticmethod
    def login(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user"""
        if not email or not password:
            st.error("⚠️ Veuillez remplir tous les champs")
            return None
        
        if not validate_email(email):
            st.error("❌ Format d'email invalide")
            return None
        
        result = UserModel.authenticate(email, password)
        
        if result and 'error' not in result:
            # Log successful login
            ActivityLogModel.log_activity(
                result['id'], None, 'connexion', 
                f"Connexion réussie pour {result['email']}"
            )
            return result
        elif result and 'error' in result:
            st.error(f"❌ {result['error']}")
        else:
            st.error("❌ Identifiants incorrects")
            
        return None
    
    @staticmethod
    def logout(user_id: int):
        """Logout user"""
        if user_id:
            ActivityLogModel.log_activity(
                user_id, None, 'deconnexion', "Déconnexion utilisateur"
            )
        
        # Clear session state
        for key in list(st.session_state.keys()):
            if key.startswith(('logged_in', 'user_', 'page')):
                del st.session_state[key]
        
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_info = {}
        st.session_state.page = "login"
    
    @staticmethod
    def check_session() -> bool:
        """Check if user session is valid"""
        return (
            st.session_state.get('logged_in', False) and 
            st.session_state.get('user_id') is not None
        )
    
    @staticmethod
    def require_auth(func):
        """Décorateur pour exiger une authentification"""
        def wrapper(*args, **kwargs):
            if not AuthController.check_session():
                st.error("❌ Vous devez être connecté pour accéder à cette page")
                st.session_state.page = "login"
                st.rerun()
                return None
            return func(*args, **kwargs)
        return wrapper
    
    @staticmethod
    def require_role(allowed_roles: list):
        """Décorateur pour exiger un rôle spécifique"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not AuthController.check_session():
                    st.error("❌ Vous devez être connecté")
                    st.session_state.page = "login"
                    st.rerun()
                    return None
                
                user_role = st.session_state.user_info.get('role')
                if user_role not in allowed_roles:
                    st.error("❌ Vous n'avez pas les permissions nécessaires")
                    st.session_state.page = "dashboard"
                    st.rerun()
                    return None
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def get_current_user() -> Optional[Dict[str, Any]]:
        """Get current logged-in user"""
        if AuthController.check_session():
            return st.session_state.user_info
        return None
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """Get current user ID"""
        if AuthController.check_session():
            return st.session_state.user_id
        return None
    
    @staticmethod
    def has_permission(permission: str) -> bool:
        """Check if current user has specific permission"""
        user = AuthController.get_current_user()
        if not user:
            return False
        
        from config.settings import has_permission
        return has_permission(user['role'], permission)
    
    @staticmethod
    def is_admin() -> bool:
        """Check if current user is admin"""
        user = AuthController.get_current_user()
        return user and user.get('role') == 'admin'
    
    @staticmethod
    def can_access_page(page: str) -> bool:
        """Check if current user can access a specific page"""
        user = AuthController.get_current_user()
        if not user:
            return False
        
        role = user['role']
        
        # Define page access rules
        page_access = {
            'dashboard': ['admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing'],
            'admin_create_demande': ['admin'],
            'nouvelle_demande': ['tc', 'dr', 'marketing'],
            'demandes': ['admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing'],
            'gestion_utilisateurs': ['admin'],
            'admin_dropdown_options': ['admin'],
            'validations': ['dr', 'dr_financier', 'dg'],
            'analytics': ['admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing'],
            'notifications': ['admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing'],
        }
        
        allowed_roles = page_access.get(page, [])
        return role in allowed_roles
