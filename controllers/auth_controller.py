"""
Authentication controller - Version Corrigée
Utilise le PermissionService centralisé pour toutes les vérifications
"""
import streamlit as st
from typing import Optional, Dict, Any
import logging
from datetime import datetime

from models.user import UserModel
from models.activity_log import ActivityLogModel
from services.permission_service import permission_service, Permission
from utils.validators import validate_email, validate_password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthController:
    """Controller for authentication operations - Version corrigée"""
    
    @staticmethod
    def login(email: str, password: str, remember_device: bool = False) -> Optional[Dict[str, Any]]:
        """Authentifier un utilisateur"""
        try:
            if not email or not password:
                st.error("⚠️ Veuillez remplir tous les champs")
                logger.warning(f"Tentative de connexion avec champs vides: {email}")
                return None
            
            if not validate_email(email):
                st.error("❌ Format d'email invalide")
                logger.warning(f"Tentative de connexion avec email invalide: {email}")
                return None
            
            result = UserModel.authenticate(email, password)
            
            if result and 'error' not in result:
                AuthController._handle_successful_login(result)
                return result
                
            elif result and 'error' in result:
                st.error(f"❌ {result['error']}")
                logger.warning(f"Connexion échouée pour {email}: {result['error']}")
            else:
                st.error("❌ Identifiants incorrects")
                logger.warning(f"Tentative de connexion échouée: {email}")
            
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la connexion: {e}")
            st.error("❌ Erreur technique lors de la connexion")
            return None
    
    @staticmethod
    def _handle_successful_login(user_info: Dict[str, Any]):
        """Traiter une connexion réussie - Utilise le gestionnaire centralisé"""
        try:
            user_id = user_info['id']
            
            UserModel.update_user(user_id, last_login=datetime.now().isoformat())
            
            ActivityLogModel.log_activity(
                user_id, None, 'connexion',
                f"Connexion réussie pour {user_info['email']}"
            )
            
            # Utiliser le gestionnaire de session centralisé
            from utils.session_manager import session_manager
            session_manager.login_user(user_id, user_info)
            
            logger.info(f"Connexion réussie: {user_info['email']} ({user_info['role']})")
            
        except Exception as e:
            logger.error(f"Erreur traitement connexion réussie: {e}")
    
    @staticmethod
    def logout(user_id: Optional[int] = None):
        """Déconnecter un utilisateur - Utilise le gestionnaire centralisé"""
        try:
            from utils.session_manager import session_manager
            
            if user_id is None:
                user_id = session_manager.get_current_user_id()
            
            if user_id:
                user_info = session_manager.get_current_user_info()
                email = user_info.get('email', 'unknown')
                
                ActivityLogModel.log_activity(
                    user_id, None, 'deconnexion', f"Déconnexion de {email}"
                )
                
                logger.info(f"Déconnexion: {email}")
            
            # Utiliser le gestionnaire de session centralisé
            session_manager.logout_user()
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            # En cas d'erreur, forcer la déconnexion
            from utils.session_manager import session_manager
            session_manager.logout_user()
    

    
    @staticmethod
    def check_session() -> bool:
        """Vérifier la validité de la session utilisateur - Utilise le gestionnaire centralisé"""
        try:
            from utils.session_manager import session_manager
            
            if not session_manager.is_authenticated():
                return False
            
            user_id = session_manager.get_current_user_id()
            user_info = session_manager.get_current_user_info()
            
            if not user_id or not user_info:
                return False
            
            user_data = UserModel.get_user_by_id(user_id)
            if not user_data or not user_data.get('is_active', False):
                logger.warning(f"Session invalide: utilisateur {user_id} inactif ou supprimé")
                session_manager.logout_user()
                return False
            
            # Mettre à jour les infos utilisateur si nécessaire
            if user_data != user_info:
                session_manager.set_state('auth', 'user_info', user_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Erreur vérification session: {e}")
            return False
    
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
    def require_permission(permission: Permission):
        """Décorateur pour exiger une permission spécifique"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not AuthController.check_session():
                    st.error("❌ Vous devez être connecté")
                    st.session_state.page = "login"
                    st.rerun()
                    return None
                
                user_role = AuthController.get_current_user_role()
                if not permission_service.has_permission(user_role, permission):
                    st.error("❌ Vous n'avez pas les permissions nécessaires")
                    st.session_state.page = "dashboard"
                    st.rerun()
                    return None
                
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
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
                
                user_role = AuthController.get_current_user_role()
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
        """Obtenir l'utilisateur actuellement connecté - Utilise le gestionnaire centralisé"""
        try:
            from utils.session_manager import session_manager
            if session_manager.is_authenticated():
                return session_manager.get_current_user_info()
            return None
        except Exception as e:
            logger.error(f"Erreur récupération utilisateur actuel: {e}")
            return None
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """Obtenir l'ID de l'utilisateur actuellement connecté - Utilise le gestionnaire centralisé"""
        try:
            from utils.session_manager import session_manager
            return session_manager.get_current_user_id()
        except Exception as e:
            logger.error(f"Erreur récupération ID utilisateur actuel: {e}")
            return None
    
    @staticmethod
    def get_current_user_role() -> Optional[str]:
        """Obtenir le rôle de l'utilisateur actuellement connecté"""
        user = AuthController.get_current_user()
        return user.get('role') if user else None
    
    @staticmethod
    def has_permission(permission: Permission) -> bool:
        """Vérifier si l'utilisateur actuel a une permission spécifique"""
        user_role = AuthController.get_current_user_role()
        if not user_role:
            return False
        
        return permission_service.has_permission(user_role, permission)
    
    @staticmethod
    def has_permission_str(permission_str: str) -> bool:
        """Vérifier si l'utilisateur actuel a une permission spécifique (version string)"""
        user_role = AuthController.get_current_user_role()
        if not user_role:
            return False
        
        return permission_service.has_permission_str(user_role, permission_str)
    
    @staticmethod
    def is_admin() -> bool:
        """Vérifier si l'utilisateur actuel est administrateur"""
        user_role = AuthController.get_current_user_role()
        return permission_service.is_admin(user_role) if user_role else False
    
    @staticmethod
    def is_validator() -> bool:
        """Vérifier si l'utilisateur actuel peut valider des demandes"""
        user_role = AuthController.get_current_user_role()
        return permission_service.is_validator(user_role) if user_role else False
    
    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
        """Change the user's password."""
        try:
            # Validate password strength if necessary (can add more checks)
            if not validate_password(new_password): # Assuming validate_password checks for basic complexity
                 return False, "Le nouveau mot de passe ne respecte pas les critères de sécurité (minimum 8 caractères, majuscule, minuscule, chiffre, caractère spécial)."

            # Call UserModel to handle the actual password change logic
            success, message = UserModel.change_password(user_id, current_password, new_password)

            if success:
                ActivityLogModel.log_activity(user_id, None, 'changement_mdp', "Mot de passe changé avec succès")
                logger.info(f"Password changed successfully for user_id: {user_id}")
                return True, "Votre mot de passe a été changé avec succès."
            else:
                # Message from UserModel explains why it failed (e.g., incorrect current password)
                ActivityLogModel.log_activity(user_id, None, 'changement_mdp_echec', f"Échec changement mot de passe: {message}")
                logger.warning(f"Password change failed for user_id: {user_id}: {message}")
                return False, message

        except Exception as e:
            logger.error(f"Error changing password for user_id {user_id}: {e}")
            ActivityLogModel.log_activity(user_id, None, 'changement_mdp_erreur', f"Erreur interne changement mot de passe: {e}")
            return False, "Une erreur interne est survenue lors du changement de mot de passe."
    
    @staticmethod
    def is_financial_validator() -> bool:
        """Vérifier si l'utilisateur actuel peut faire des validations financières"""
        user_role = AuthController.get_current_user_role()
        return permission_service.is_financial_validator(user_role) if user_role else False
    
    @staticmethod
    def can_access_page(page: str) -> bool:
        """Vérifier si l'utilisateur actuel peut accéder à une page"""
        user_role = AuthController.get_current_user_role()
        if not user_role:
            return False
        
        return permission_service.can_access_page(user_role, page)
    
    @staticmethod
    def can_validate_demande(demande_status: str, demande_user_id: int, 
                           directeur_id: Optional[int] = None) -> bool:
        """Vérifier si l'utilisateur actuel peut valider une demande"""
        user = AuthController.get_current_user()
        if not user:
            return False
        
        return permission_service.can_validate_demande(
            user['role'], demande_status, user['id'], demande_user_id, directeur_id
        )
    
    @staticmethod
    def can_edit_demande(demande_status: str, demande_user_id: int) -> bool:
        """Vérifier si l'utilisateur actuel peut modifier une demande"""
        user = AuthController.get_current_user()
        if not user:
            return False
        
        return permission_service.can_edit_demande(
            user['role'], demande_status, user['id'], demande_user_id
        )
    
    @staticmethod
    def can_view_demande(demande_user_id: int, demande_participants: list = None, 
                        directeur_id: Optional[int] = None) -> bool:
        """Vérifier si l'utilisateur actuel peut voir une demande"""
        user = AuthController.get_current_user()
        if not user:
            return False
        
        return permission_service.can_view_demande(
            user['role'], user['id'], demande_user_id, 
            demande_participants or [], directeur_id
        )
    
    @staticmethod
    def get_accessible_pages() -> list:
        """Obtenir la liste des pages accessibles à l'utilisateur actuel"""
        user_role = AuthController.get_current_user_role()
        if not user_role:
            return []
        
        return permission_service.get_accessible_pages(user_role)
    
    @staticmethod
    def get_user_permissions() -> list:
        """Obtenir la liste des permissions de l'utilisateur actuel"""
        user_role = AuthController.get_current_user_role()
        if not user_role:
            return []
        
        return permission_service.get_user_permissions(user_role)
