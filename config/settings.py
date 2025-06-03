"""
Configuration settings for BudgetManage application
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Configuration for database"""
    name: str = "budget_workflow.db"
    path: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "budget_workflow.db")

@dataclass
class EmailConfig:
    """Configuration for email notifications"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email: str = os.getenv("EMAIL_ADDRESS", "votre-email@gmail.com")
    password: str = os.getenv("EMAIL_PASSWORD", "votre-mot-de-passe-app")
    use_outlook: bool = True  # Use Outlook COM instead of SMTP

@dataclass
class AppConfig:
    """General application configuration"""
    page_title: str = "Système de Gestion Budget"
    page_icon: str = "💰"
    layout: str = "wide"
    initial_sidebar_state: str = "expanded"
    
    # Security
    min_password_length: int = 8
    
    # Pagination
    default_page_size: int = 10
    max_notifications: int = 20
    
    # File uploads (for future use)
    max_file_size_mb: int = 10
    allowed_file_types: list = None
    
    def __post_init__(self):
        if self.allowed_file_types is None:
            self.allowed_file_types = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.jpg', '.png']

@dataclass
class RoleConfig:
    """Role-based configuration"""
    roles: dict = None
    
    def __post_init__(self):
        if self.roles is None:
            self.roles = {
                'admin': {
                    'label': 'Administrateur',
                    'permissions': ['create_user', 'activate_user', 'view_all', 'system_config'],
                    'color': '#ff6b6b'
                },
                'tc': {
                    'label': 'Technico-Commercial',
                    'permissions': ['create_budget_request', 'view_own'],
                    'color': '#74b9ff'
                },
                'dr': {
                    'label': 'Directeur Régional',
                    'permissions': ['create_budget_request', 'validate_tc_requests', 'view_team'],
                    'color': '#fdcb6e'
                },
                'dr_financier': {
                    'label': 'Directeur Financier',
                    'permissions': ['validate_financial', 'view_financial'],
                    'color': '#a29bfe'
                },
                'dg': {
                    'label': 'Directeur Général',
                    'permissions': ['validate_financial', 'view_all', 'strategic_view'],
                    'color': '#fd79a8'
                },
                'marketing': {
                    'label': 'Marketing',
                    'permissions': ['create_marketing_request', 'view_own'],
                    'color': '#55efc4'
                }
            }

# Configuration instances
db_config = DatabaseConfig()
email_config = EmailConfig()
app_config = AppConfig()
role_config = RoleConfig()

# Status configuration
STATUS_CONFIG = {
    'brouillon': {
        'label': 'Brouillon',
        'color': '#6c757d',
        'icon': '📝'
    },
    'en_attente_dr': {
        'label': 'Attente DR',
        'color': '#ffc107',
        'icon': '⏳'
    },
    'en_attente_financier': {
        'label': 'Attente Financier',
        'color': '#fd7e14',
        'icon': '💰'
    },
    'validee': {
        'label': 'Validée',
        'color': '#28a745',
        'icon': '✅'
    },
    'rejetee': {
        'label': 'Rejetée',
        'color': '#dc3545',
        'icon': '❌'
    }
}

# Workflow configuration
WORKFLOW_CONFIG = {
    'budget': {
        'tc': 'en_attente_dr',
        'dr': 'en_attente_financier',
        'dr_financier': 'validee',
        'dg': 'validee'
    },
    'marketing': {
        'marketing': 'en_attente_financier',
        'dr_financier': 'validee',
        'dg': 'validee',
        'admin': 'validee'
    }
}

def get_role_label(role: str) -> str:
    """Get human-readable role label"""
    return role_config.roles.get(role, {}).get('label', role)

def get_role_color(role: str) -> str:
    """Get role color for UI"""
    return role_config.roles.get(role, {}).get('color', '#6c757d')

def get_status_info(status: str) -> dict:
    """Get status information for UI"""
    return STATUS_CONFIG.get(status, {
        'label': status,
        'color': '#6c757d',
        'icon': '❓'
    })

def has_permission(role: str, permission: str) -> bool:
    """Check if role has specific permission"""
    role_info = role_config.roles.get(role, {})
    return permission in role_info.get('permissions', [])
