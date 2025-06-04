"""
Service de permissions compatible avec AuthController - Version Corrigée
"""
from enum import Enum
from typing import Dict, List, Optional

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

class PermissionService:
    """Service centralisé pour la gestion des permissions"""
    
    # Matrice des permissions par rôle
    ROLE_PERMISSIONS = {
        'admin': [
            Permission.CREATE_USER, Permission.EDIT_USER, Permission.DELETE_USER,
            Permission.ACTIVATE_USER, Permission.VIEW_ALL_USERS,
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE, Permission.EDIT_ANY_DEMANDE,
            Permission.DELETE_DEMANDE, Permission.VIEW_OWN_DEMANDES, Permission.VIEW_TEAM_DEMANDES,
            Permission.VIEW_ALL_DEMANDES, Permission.ADMIN_CREATE_DEMANDE,
            Permission.VALIDATE_DR, Permission.VALIDATE_FINANCIAL, Permission.VALIDATE_DG,
            Permission.SYSTEM_CONFIG, Permission.VIEW_ANALYTICS, Permission.MANAGE_DROPDOWN_OPTIONS,
        ],
        'tc': [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_ANALYTICS,
        ],
        'dr': [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_TEAM_DEMANDES,
            Permission.VIEW_ANALYTICS, Permission.VALIDATE_DR,
        ],
        'dr_financier': [
            Permission.VIEW_ALL_DEMANDES, Permission.VIEW_ANALYTICS,
            Permission.VALIDATE_FINANCIAL,
        ],
        'dg': [
            Permission.VIEW_ALL_DEMANDES, Permission.VIEW_ANALYTICS,
            Permission.VALIDATE_FINANCIAL, Permission.VALIDATE_DG,
        ],
        'marketing': [
            Permission.CREATE_DEMANDE, Permission.EDIT_OWN_DEMANDE,
            Permission.VIEW_OWN_DEMANDES, Permission.VIEW_ANALYTICS,
        ]
    }
    
    # Pages accessibles par rôle
    ROLE_PAGES = {
        'admin': [
            'dashboard', 'admin_create_demande', 'demandes', 'gestion_utilisateurs',
            'admin_dropdown_options', 'gestion_budgets', 'validations', 'analytics', 'notifications', 'account_settings'
        ],
        'tc': [
            'dashboard', 'nouvelle_demande', 'demandes', 'analytics', 'notifications', 'account_settings'
        ],
        'dr': [
            'dashboard', 'nouvelle_demande', 'demandes', 'validations', 'analytics', 'notifications', 'account_settings'
        ],
        'dr_financier': [
            'dashboard', 'demandes', 'validations', 'analytics', 'notifications', 'account_settings'
        ],
        'dg': [
            'dashboard', 'demandes', 'validations', 'analytics', 'notifications', 'account_settings'
        ],
        'marketing': [
            'dashboard', 'nouvelle_demande', 'demandes', 'analytics', 'notifications', 'account_settings'
        ]
    }
    
    @staticmethod
    def has_permission(user_role: str, permission: Permission) -> bool:
        """Vérifier si un rôle a une permission spécifique"""
        return permission in PermissionService.ROLE_PERMISSIONS.get(user_role, [])
    
    @staticmethod
    def has_permission_str(user_role: str, permission_str: str) -> bool:
        """Vérifier si un rôle a une permission spécifique (version string)"""
        try:
            permission = Permission(permission_str)
            return PermissionService.has_permission(user_role, permission)
        except ValueError:
            return False
    
    @staticmethod
    def can_access_page(user_role: str, page: str) -> bool:
        """Vérifier si un rôle peut accéder à une page"""
        return page in PermissionService.ROLE_PAGES.get(user_role, [])
    
    @staticmethod
    def can_validate_demande(user_role: str, demande_status: str, user_id: int, 
                           demande_user_id: int, directeur_id: Optional[int] = None) -> bool:
        """Vérifier si un utilisateur peut valider une demande"""
        if demande_status == 'en_attente_dr':
            if user_role != 'dr':
                return False
            return user_id == demande_user_id or user_id == directeur_id
        
        elif demande_status == 'en_attente_financier':
            return user_role in ['dr_financier', 'dg', 'admin']
        
        return False
    
    @staticmethod
    def can_edit_demande(user_role: str, demande_status: str, user_id: int, 
                        demande_user_id: int) -> bool:
        """Vérifier si un utilisateur peut modifier une demande"""
        if PermissionService.has_permission(user_role, Permission.EDIT_ANY_DEMANDE):
            return True
        
        if not PermissionService.has_permission(user_role, Permission.EDIT_OWN_DEMANDE):
            return False
        
        if user_id != demande_user_id:
            return False
        
        return demande_status == 'brouillon'
    
    @staticmethod
    def can_view_demande(user_role: str, user_id: int, demande_user_id: int, 
                        demande_participants: List[int] = None, 
                        directeur_id: Optional[int] = None) -> bool:
        """Vérifier si un utilisateur peut voir une demande"""
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
    
    @staticmethod
    def is_admin(user_role: str) -> bool:
        """Vérifier si l'utilisateur est admin"""
        return user_role == 'admin'
    
    @staticmethod
    def is_validator(user_role: str) -> bool:
        """Vérifier si l'utilisateur peut valider des demandes"""
        return user_role in ['dr', 'dr_financier', 'dg', 'admin']
    
    @staticmethod
    def is_financial_validator(user_role: str) -> bool:
        """Vérifier si l'utilisateur peut faire des validations financières"""
        return user_role in ['dr_financier', 'dg', 'admin']
    
    @staticmethod
    def get_accessible_pages(user_role: str) -> List[str]:
        """Obtenir toutes les pages accessibles pour un rôle"""
        return PermissionService.ROLE_PAGES.get(user_role, [])
    
    @staticmethod
    def get_user_permissions(user_role: str) -> List[str]:
        """Obtenir toutes les permissions d'un rôle"""
        permissions = PermissionService.ROLE_PERMISSIONS.get(user_role, [])
        return [perm.value for perm in permissions]

# Instance globale du service de permissions
permission_service = PermissionService()
