"""
Gestionnaire de session centralisé pour Streamlit - Version Corrigée
"""
import streamlit as st
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Gestionnaire centralisé de la session Streamlit"""
    
    def __init__(self):
        self.auth_key = 'auth'
        self.nav_key = 'navigation'
        self.app_key = 'app_state'
    
    def init_session(self):
        """Initialiser la session avec les états par défaut"""
        try:
            # État d'authentification
            if self.auth_key not in st.session_state:
                st.session_state[self.auth_key] = {
                    'logged_in': False,
                    'user_id': None,
                    'user_info': {}
                }
            
            # État de navigation
            if self.nav_key not in st.session_state:
                st.session_state[self.nav_key] = {
                    'current_page': 'dashboard'
                }
            
            # État de l'application
            if self.app_key not in st.session_state:
                st.session_state[self.app_key] = {
                    'initialized': False,
                    'theme': 'light',
                    'notifications_count': 0
                }
            
            logger.debug("Session initialisée avec succès")
            
        except Exception as e:
            logger.error(f"Erreur initialisation session: {e}")
    
    def login_user(self, user_id: int, user_info: dict):
        """Connecter un utilisateur"""
        try:
            st.session_state[self.auth_key] = {
                'logged_in': True,
                'user_id': user_id,
                'user_info': user_info
            }
            
            # Rediriger vers le dashboard après connexion
            st.session_state[self.nav_key]['current_page'] = 'dashboard'
            
            logger.info(f"Utilisateur connecté: {user_info.get('email', 'unknown')}")
            
        except Exception as e:
            logger.error(f"Erreur connexion utilisateur: {e}")
    
    def logout_user(self):
        """Déconnecter l'utilisateur"""
        try:
            # Conserver l'email pour les logs
            current_user = self.get_current_user_info()
            email = current_user.get('email', 'unknown')
            
            # Réinitialiser l'état d'authentification
            st.session_state[self.auth_key] = {
                'logged_in': False,
                'user_id': None,
                'user_info': {}
            }
            
            # Rediriger vers la page de connexion
            st.session_state[self.nav_key]['current_page'] = 'login'
            
            # Nettoyer les autres états de session si nécessaire
            keys_to_preserve = {self.auth_key, self.nav_key, self.app_key}
            keys_to_remove = []
            
            for key in st.session_state.keys():
                if key not in keys_to_preserve:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                try:
                    del st.session_state[key]
                except:
                    pass
            
            logger.info(f"Utilisateur déconnecté: {email}")
            
        except Exception as e:
            logger.error(f"Erreur déconnexion utilisateur: {e}")
    
    def is_authenticated(self) -> bool:
        """Vérifier si l'utilisateur est connecté"""
        try:
            auth_state = st.session_state.get(self.auth_key, {})
            return auth_state.get('logged_in', False) and auth_state.get('user_id') is not None
        except Exception as e:
            logger.error(f"Erreur vérification authentification: {e}")
            return False
    
    def get_current_user_id(self) -> Optional[int]:
        """Obtenir l'ID de l'utilisateur connecté"""
        try:
            auth_state = st.session_state.get(self.auth_key, {})
            return auth_state.get('user_id')
        except Exception as e:
            logger.error(f"Erreur récupération user_id: {e}")
            return None
    
    def get_current_user_info(self) -> Dict[str, Any]:
        """Obtenir les informations de l'utilisateur connecté"""
        try:
            auth_state = st.session_state.get(self.auth_key, {})
            return auth_state.get('user_info', {})
        except Exception as e:
            logger.error(f"Erreur récupération user_info: {e}")
            return {}
    
    def get_current_page(self) -> str:
        """Obtenir la page actuelle"""
        try:
            nav_state = st.session_state.get(self.nav_key, {})
            return nav_state.get('current_page', 'dashboard')
        except Exception as e:
            logger.error(f"Erreur récupération page actuelle: {e}")
            return 'dashboard'
    
    def set_current_page(self, page: str):
        """Définir la page actuelle"""
        try:
            if self.nav_key not in st.session_state:
                st.session_state[self.nav_key] = {}
            
            st.session_state[self.nav_key]['current_page'] = page
            logger.debug(f"Page définie: {page}")
            
        except Exception as e:
            logger.error(f"Erreur définition page: {e}")
    
    def set_state(self, category: str, key: str, value: Any):
        """Définir une valeur dans un état spécifique"""
        try:
            if category not in st.session_state:
                st.session_state[category] = {}
            
            st.session_state[category][key] = value
            logger.debug(f"État défini: {category}.{key} = {value}")
            
        except Exception as e:
            logger.error(f"Erreur définition état: {e}")
    
    def get_state(self, category: str, key: str, default: Any = None) -> Any:
        """Obtenir une valeur d'un état spécifique"""
        try:
            category_state = st.session_state.get(category, {})
            return category_state.get(key, default)
        except Exception as e:
            logger.error(f"Erreur récupération état: {e}")
            return default
    
    def clear_state(self, category: str):
        """Nettoyer un état spécifique"""
        try:
            if category in st.session_state:
                del st.session_state[category]
                logger.debug(f"État nettoyé: {category}")
        except Exception as e:
            logger.error(f"Erreur nettoyage état: {e}")
    
    def update_user_info(self, user_info: dict):
        """Mettre à jour les informations utilisateur"""
        try:
            if self.auth_key in st.session_state:
                st.session_state[self.auth_key]['user_info'] = user_info
                logger.debug("Informations utilisateur mises à jour")
        except Exception as e:
            logger.error(f"Erreur mise à jour user_info: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Obtenir un résumé de l'état de la session (pour debug)"""
        try:
            return {
                'authenticated': self.is_authenticated(),
                'user_id': self.get_current_user_id(),
                'user_email': self.get_current_user_info().get('email', 'N/A'),
                'current_page': self.get_current_page(),
                'session_keys': list(st.session_state.keys())
            }
        except Exception as e:
            logger.error(f"Erreur résumé session: {e}")
            return {'error': str(e)}

# Instance globale du gestionnaire de session
session_manager = SessionManager()
