"""
Permission Service - Centralisation des permissions
Service centralisé pour gérer toutes les permissions de l'application
"""
from typing import Dict, List, Optional, Any
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class Permission(Enum):
    """Énumération des permissions disponibles"""
    # Permissions utilisateurs
    CREATE_USER = "create_user"
    EDIT_USER = "edit_user"
    DELETE_USER = "delete_user"
    ACTIVATE_USER = "activate_user"
    VIEW_ALL_USERS = "view_all_users"
    
    # Permissions demandes
    CREATE_DEMANDE = "create_demande"
    EDIT_OWN_DEMANDE = "edit_own_demande"
    EDIT_ANY_DEMANDE = "edit_any_demande"
    DELETE_DEMANDE = "delete_demande"
    VIEW_OWN_DEMANDES = "view_own_demandes"
    VIEW_TEAM_DEMANDES = "view_team_demandes"
    VIEW_ALL_DEMANDES = "view_all_demandes"
    
    # Permissions validations
    VALIDATE_DR = "validate_dr"
    VALIDATE_FINANCIAL = "validate_financial"
    VALIDATE_DG = "validate_dg"
    
    # Permissions système
    SYSTEM_CONFIG = "system_config"
    VIEW_ANALYTICS = "view_analytics"
    ADMIN_CREATE_DEMANDE = "admin_create_demande"
    MANAGE_DROPDOWN_OPTIONS = "manage_dropdown_options"

class Role(Enum):
    """Énumération des rôles"""
    ADMIN = "admin"
    TC = "tc"
    DR = "dr"
    DR_FINANCIER = "dr_financier"
    DG = "dg"
    MARKETING = "marketing"

class PermissionService:
    """Service centralisé pour la gestion des permissions"""
    
    # Matrice des permissions par rôle
    _ROLE_PERMISSIONS = {
        Role.ADMIN: [
            Permission.CREATE_USER, Permission.EDIT_USER, Permission.DELETE_USER,
            Permission.ACTIVATE_USER, Permission.VIEW_ALL_USERS,
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE, Permission.EDIT_ANY_DEMANDE,
            Permission.DELETE_DEMANDE, Permission.VIEW_OWN_DEMANDES, Permission.VIEW_TEAM_DEMANDES,
            Permission.VIEW_ALL_DEMANDES, Permission.ADMIN_CREATE_DEMANDE,
            Permission.VALIDATE_DR, Permission.VALIDATE_FINANCIAL, Permission.VALIDATE_DG,
            Permission.SYSTEM_CONFIG, Permission.VIEW_ANALYTICS, Permission.MANAGE_DROPDOWN_OPTIONS,
        ],
        Role.TC: [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_ANALYTICS,
        ],
        Role.DR: [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_TEAM_DEMANDES,
            Permission.VIEW_ANALYTICS, Permission.VALIDATE_DR,
        ],
        Role.DR_FINANCIER: [
            Permission.VIEW_ALL_DEMANDES, Permission.VIEW_ANALYTICS,
            Permission.VALIDATE_FINANCIAL,
        ],
        Role.DG: [
            Permission.VIEW_ALL_DEMANDES, Permission.VIEW_ANALYTICS,
            Permission.VALIDATE_FINANCIAL, Permission.VALIDATE_DG,
        ],
        Role.MARKETING: [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_ANALYTICS,
        ]
    }
    
    # Pages accessibles par rôle
    _ROLE_PAGES = {
        Role.ADMIN: [
            'dashboard', 'admin_create_demande', 'demandes', 'gestion_utilisateurs',
            'admin_dropdown_options', 'validations', 'analytics', 'notifications'
        ],
        Role.TC: [
            'dashboard', 'nouvelle_demande', 'demandes', 'analytics', 'notifications'
        ],
        Role.DR: [
            'dashboard', 'nouvelle_demande', 'demandes', 'validations', 'analytics', 'notifications'
        ],
        Role.DR_FINANCIER: [
            'dashboard', 'demandes', 'validations', 'analytics', 'notifications'
        ],
        Role.DG: [
            'dashboard', 'demandes', 'validations', 'analytics', 'notifications'
        ],
        Role.MARKETING: [
            'dashboard', 'nouvelle_demande', 'demandes', 'analytics', 'notifications'
        ]
    }
    
    @staticmethod
    def has_permission(user_role: str, permission: Permission) -> bool:
        """Vérifier si un rôle a une permission spécifique"""
        try:
            role = Role(user_role)
            return permission in PermissionService._ROLE_PERMISSIONS.get(role, [])
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return False
    
    @staticmethod
    def has_permission_str(user_role: str, permission_str: str) -> bool:
        """Vérifier si un rôle a une permission spécifique (version string)"""
        try:
            permission = Permission(permission_str)
            return PermissionService.has_permission(user_role, permission)
        except ValueError:
            logger.error(f"Permission inconnue: {permission_str}")
            return False
    
    @staticmethod
    def can_access_page(user_role: str, page: str) -> bool:
        """Vérifier si un rôle peut accéder à une page"""
        try:
            role = Role(user_role)
            return page in PermissionService._ROLE_PAGES.get(role, [])
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return False
    
    @staticmethod
    def can_validate_demande(user_role: str, demande_status: str, user_id: int, 
                           demande_user_id: int, directeur_id: Optional[int] = None) -> bool:
        """Vérifier si un utilisateur peut valider une demande"""
        try:
            role = Role(user_role)
            
            if demande_status == 'en_attente_dr':
                if role != Role.DR:
                    return False
                return user_id == demande_user_id or user_id == directeur_id
            
            elif demande_status == 'en_attente_financier':
                return role in [Role.DR_FINANCIER, Role.DG, Role.ADMIN]
            
            return False
            
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return False
    
    @staticmethod
    def can_edit_demande(user_role: str, demande_status: str, user_id: int, 
                        demande_user_id: int) -> bool:
        """Vérifier si un utilisateur peut modifier une demande"""
        try:
            if PermissionService.has_permission(user_role, Permission.EDIT_ANY_DEMANDE):
                return True
            
            if not PermissionService.has_permission(user_role, Permission.EDIT_OWN_DEMANDE):
                return False
            
            if user_id != demande_user_id:
                return False
            
            return demande_status == 'brouillon'
            
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return False
    
    @staticmethod
    def can_view_demande(user_role: str, user_id: int, demande_user_id: int, 
                        demande_participants: List[int] = None, 
                        directeur_id: Optional[int] = None) -> bool:
        """Vérifier si un utilisateur peut voir une demande"""
        try:
            if PermissionService.has_permission(user_role, Permission.VIEW_ALL_DEMANDES):
                return True
            
            if user_id == demande_user_id:
                return True
            
            if (PermissionService.has_permission(user_role, Permission.VIEW_TEAM_DEMANDES) 
                and user_id == directeur_id):
                return True
            
            if demande_participants and user_id in demande_participants:
                return True
            
            return False
            
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return False
    
    @staticmethod
    def get_user_permissions(user_role: str) -> List[str]:
        """Obtenir toutes les permissions d'un rôle"""
        try:
            role = Role(user_role)
            permissions = PermissionService._ROLE_PERMISSIONS.get(role, [])
            return [perm.value for perm in permissions]
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return []
    
    @staticmethod
    def get_accessible_pages(user_role: str) -> List[str]:
        """Obtenir toutes les pages accessibles pour un rôle"""
        try:
            role = Role(user_role)
            return PermissionService._ROLE_PAGES.get(role, [])
        except ValueError:
            logger.error(f"Rôle inconnu: {user_role}")
            return []
    
    @staticmethod
    def is_admin(user_role: str) -> bool:
        """Vérifier si l'utilisateur est admin"""
        return user_role == Role.ADMIN.value
    
    @staticmethod
    def is_validator(user_role: str) -> bool:
        """Vérifier si l'utilisateur peut valider des demandes"""
        return user_role in [Role.DR.value, Role.DR_FINANCIER.value, Role.DG.value, Role.ADMIN.value]
    
    @staticmethod
    def is_financial_validator(user_role: str) -> bool:
        """Vérifier si l'utilisateur peut faire des validations financières"""
        return user_role in [Role.DR_FINANCIER.value, Role.DG.value, Role.ADMIN.value]
    
    @staticmethod
    def get_role_label(role: str) -> str:
        """Obtenir le libellé d'un rôle"""
        role_labels = {
            Role.ADMIN.value: 'Administrateur',
            Role.TC.value: 'Technico-Commercial',
            Role.DR.value: 'Directeur Régional',
            Role.DR_FINANCIER.value: 'Directeur Financier',
            Role.DG.value: 'Directeur Général',
            Role.MARKETING.value: 'Marketing'
        }
        return role_labels.get(role, role)
    
    @staticmethod
    def get_role_color(role: str) -> str:
        """Obtenir la couleur d'un rôle pour l'UI"""
        role_colors = {
            Role.ADMIN.value: '#ff6b6b',
            Role.TC.value: '#74b9ff',
            Role.DR.value: '#fdcb6e',
            Role.DR_FINANCIER.value: '#a29bfe',
            Role.DG.value: '#fd79a8',
            Role.MARKETING.value: '#55efc4'
        }
        return role_colors.get(role, '#6c757d')

# Instance globale du service de permissions
permission_service = PermissionService()
