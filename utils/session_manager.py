"""
Gestionnaire centralisé pour l'état de session Streamlit
Évite la duplication et les conflits de variables d'état
"""
import streamlit as st
from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class SessionManager:
    """Gestionnaire centralisé pour l'état de session Streamlit"""
    
    # Configuration des variables d'état par page/composant
    _SESSION_CONFIG = {
        'auth': {
            'logged_in': False,
            'user_id': None,
            'user_info': {},
            'page': 'login'
        },
        'demandes': {
            'search_query': '',
            'status_filter': 'tous',
            'urgence_filter': 'toutes',
            'montant_filter': 'tous',
            'type_filter': 'tous',
            'sort_by': 'updated_at',
            'sort_order': 'desc',
            'page_size': 10,
            'current_page': 1
        },
        'validations': {
            'search_query': '',
            'urgence_filter': 'toutes',
            'montant_filter': 'tous',
            'type_filter': 'tous',
            'sort_by': 'urgence',
            'sort_order': 'asc'
        },
        'users': {
            'search_query': '',
            'role_filter': 'tous',
            'status_filter': 'tous',
            'region_filter': 'toutes',
            'sort_by': 'created_at',
            'sort_order': 'desc'
        },
        'analytics': {
            'date_range': '3mois',
            'region_filter': 'toutes',
            'type_filter': 'tous',
            'chart_type': 'evolution'
        },
        'notifications': {
            'filter_read': 'non_lues',
            'type_filter': 'tous',
            'sort_by': 'created_at',
            'sort_order': 'desc'
        }
    }
    
    @staticmethod
    def init_session(component: str = None):
        \"\"\"
        Initialise les variables d'état pour un composant spécifique ou tous
        
        Args:
            component: Nom du composant ('auth', 'demandes', etc.) ou None pour tous
        \"\"\"
        try:
            if component:
                # Initialiser un composant spécifique
                if component in SessionManager._SESSION_CONFIG:
                    config = SessionManager._SESSION_CONFIG[component]
                    SessionManager._init_component_state(component, config)
                else:
                    logger.warning(f\"Composant inconnu: {component}\")
            else:
                # Initialiser tous les composants
                for comp_name, comp_config in SessionManager._SESSION_CONFIG.items():
                    SessionManager._init_component_state(comp_name, comp_config)
                    
        except Exception as e:
            logger.error(f\"Erreur initialisation session: {e}\")
    
    @staticmethod
    def _init_component_state(component: str, config: Dict[str, Any]):
        \"\"\"Initialise l'état pour un composant spécifique\"\"\"
        for key, default_value in config.items():
            session_key = f\"{component}_{key}\"
            if session_key not in st.session_state:
                st.session_state[session_key] = default_value
    
    @staticmethod
    def get_state(component: str, key: str, default: Any = None) -> Any:
        \"\"\"
        Récupère une valeur d'état de session
        
        Args:
            component: Nom du composant
            key: Clé de la variable
            default: Valeur par défaut si non trouvée
            
        Returns:
            Valeur de la variable d'état
        \"\"\"
        try:
            session_key = f\"{component}_{key}\"
            return st.session_state.get(session_key, default)
        except Exception as e:
            logger.error(f\"Erreur récupération état {component}.{key}: {e}\")
            return default
    
    @staticmethod
    def set_state(component: str, key: str, value: Any):
        \"\"\"
        Définit une valeur d'état de session
        
        Args:
            component: Nom du composant
            key: Clé de la variable
            value: Nouvelle valeur
        \"\"\"
        try:
            session_key = f\"{component}_{key}\"
            st.session_state[session_key] = value
        except Exception as e:
            logger.error(f\"Erreur définition état {component}.{key}: {e}\")
    
    @staticmethod
    def reset_component(component: str):
        \"\"\"
        Remet à zéro l'état d'un composant aux valeurs par défaut
        
        Args:
            component: Nom du composant à réinitialiser
        \"\"\"
        try:
            if component in SessionManager._SESSION_CONFIG:
                config = SessionManager._SESSION_CONFIG[component]
                for key, default_value in config.items():
                    SessionManager.set_state(component, key, default_value)
            else:
                logger.warning(f\"Composant inconnu pour reset: {component}\")
        except Exception as e:
            logger.error(f\"Erreur reset composant {component}: {e}\")
    
    @staticmethod
    def get_all_component_state(component: str) -> Dict[str, Any]:
        \"\"\"
        Récupère tout l'état d'un composant
        
        Args:
            component: Nom du composant
            
        Returns:
            Dictionnaire avec toutes les variables du composant
        \"\"\"
        try:
            if component not in SessionManager._SESSION_CONFIG:
                return {}
            
            state = {}
            config = SessionManager._SESSION_CONFIG[component]
            
            for key in config.keys():
                state[key] = SessionManager.get_state(component, key)
            
            return state
            
        except Exception as e:
            logger.error(f\"Erreur récupération état complet {component}: {e}\")
            return {}
    
    @staticmethod
    def update_component_state(component: str, updates: Dict[str, Any]):
        \"\"\"
        Met à jour plusieurs variables d'un composant
        
        Args:
            component: Nom du composant
            updates: Dictionnaire avec les nouvelles valeurs
        \"\"\"
        try:
            for key, value in updates.items():
                SessionManager.set_state(component, key, value)
        except Exception as e:
            logger.error(f\"Erreur mise à jour état {component}: {e}\")
    
    @staticmethod
    def clear_session_except_auth():
        \"\"\"Nettoie toute la session sauf l'authentification\"\"\"
        try:
            # Sauvegarder les données d'auth
            auth_data = SessionManager.get_all_component_state('auth')
            
            # Nettoyer tous les états
            keys_to_remove = []
            for key in st.session_state.keys():
                if not key.startswith('auth_'):
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del st.session_state[key]
            
            # Restaurer l'auth et réinitialiser les autres composants
            SessionManager.update_component_state('auth', auth_data)
            
            # Réinitialiser les autres composants
            for component in SessionManager._SESSION_CONFIG.keys():
                if component != 'auth':
                    SessionManager.reset_component(component)
                    
        except Exception as e:
            logger.error(f\"Erreur nettoyage session: {e}\")
    
    @staticmethod
    def is_authenticated() -> bool:
        \"\"\"Vérifie si l'utilisateur est authentifié\"\"\"
        return SessionManager.get_state('auth', 'logged_in', False)
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        \"\"\"Récupère l'ID de l'utilisateur connecté\"\"\"
        return SessionManager.get_state('auth', 'user_id')
    
    @staticmethod
    def get_current_user_info() -> Dict[str, Any]:
        \"\"\"Récupère les informations de l'utilisateur connecté\"\"\"
        return SessionManager.get_state('auth', 'user_info', {})
    
    @staticmethod
    def get_current_page() -> str:
        \"\"\"Récupère la page actuelle\"\"\"
        return SessionManager.get_state('auth', 'page', 'login')
    
    @staticmethod
    def set_current_page(page: str):
        \"\"\"Définit la page actuelle\"\"\"
        SessionManager.set_state('auth', 'page', page)
    
    @staticmethod
    def login_user(user_id: int, user_info: Dict[str, Any]):
        \"\"\"Connecte un utilisateur\"\"\"
        SessionManager.update_component_state('auth', {
            'logged_in': True,
            'user_id': user_id,
            'user_info': user_info,
            'page': 'dashboard'
        })
    
    @staticmethod
    def logout_user():
        \"\"\"Déconnecte l'utilisateur\"\"\"
        SessionManager.clear_session_except_auth()
        SessionManager.update_component_state('auth', {
            'logged_in': False,
            'user_id': None,
            'user_info': {},
            'page': 'login'
        })
    
    @staticmethod
    def create_filter_widget(component: str, filter_key: str, label: str, 
                           options: List[str], format_func=None, key_suffix: str = \"\") -> str:
        \"\"\"
        Crée un widget de filtre standardisé
        
        Args:
            component: Nom du composant
            filter_key: Clé du filtre dans la configuration
            label: Label du widget
            options: Liste des options
            format_func: Fonction de formatage des options
            key_suffix: Suffixe pour le key Streamlit
            
        Returns:
            Valeur sélectionnée
        \"\"\"
        try:
            current_value = SessionManager.get_state(component, filter_key, options[0])
            
            # S'assurer que la valeur actuelle est dans les options
            if current_value not in options:
                current_value = options[0]
                SessionManager.set_state(component, filter_key, current_value)
            
            # Widget key unique
            widget_key = f\"{component}_{filter_key}_select{key_suffix}\"
            
            selected = st.selectbox(
                label,
                options=options,
                index=options.index(current_value),
                format_func=format_func,
                key=widget_key
            )
            
            # Mettre à jour si changement
            if selected != current_value:
                SessionManager.set_state(component, filter_key, selected)
            
            return selected
            
        except Exception as e:
            logger.error(f\"Erreur création widget filtre {component}.{filter_key}: {e}\")
            return options[0] if options else \"\"
    
    @staticmethod
    def create_search_widget(component: str, placeholder: str = \"Rechercher...\", 
                           key_suffix: str = \"\") -> str:
        \"\"\"
        Crée un widget de recherche standardisé
        
        Args:
            component: Nom du composant
            placeholder: Texte placeholder
            key_suffix: Suffixe pour le key Streamlit
            
        Returns:
            Terme de recherche
        \"\"\"
        try:
            current_value = SessionManager.get_state(component, 'search_query', '')
            widget_key = f\"{component}_search_input{key_suffix}\"
            
            search = st.text_input(
                \"Rechercher\",
                value=current_value,
                placeholder=placeholder,
                key=widget_key
            )
            
            # Mettre à jour si changement
            if search != current_value:
                SessionManager.set_state(component, 'search_query', search)
            
            return search
            
        except Exception as e:
            logger.error(f\"Erreur création widget recherche {component}: {e}\")
            return \"\"
    
    @staticmethod
    def create_filter_buttons(component: str) -> tuple[bool, bool]:
        \"\"\"
        Crée les boutons de filtre standardisés (Actualiser/Effacer)
        
        Args:
            component: Nom du composant
            
        Returns:
            Tuple (refresh_clicked, clear_clicked)
        \"\"\"
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                refresh = st.button(
                    \"🔄 Actualiser\",
                    use_container_width=True,
                    key=f\"{component}_refresh\"
                )
            
            with col2:
                clear = st.button(
                    \"🗑️ Effacer Filtres\",
                    use_container_width=True,
                    key=f\"{component}_clear\"
                )
            
            if clear:
                SessionManager.reset_component(component)
            
            return refresh, clear
            
        except Exception as e:
            logger.error(f\"Erreur création boutons filtre {component}: {e}\")
            return False, False

# Instance globale du gestionnaire de session
session_manager = SessionManager()
