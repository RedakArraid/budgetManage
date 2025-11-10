#!/usr/bin/env python3
"""
Script d'application automatique des corrections BudgetManage
Ce script applique toutes les corrections identifiées de manière sécurisée.

Usage: python apply_corrections.py
"""

import os
import sys
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

class BudgetManageCorrector:
    """Classe pour appliquer les corrections BudgetManage"""
    
    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()
        self.backup_dir = self.project_path / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.success_count = 0
        self.error_count = 0
        
    def log(self, message, level="INFO"):
        """Logger simple"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
    
    def create_backup(self):
        """Créer une sauvegarde complète"""
        try:
            self.log("🔄 Création de la sauvegarde...")
            
            # Créer le dossier de backup
            self.backup_dir.mkdir(exist_ok=True)
            
            # Sauvegarder la base de données
            db_path = self.project_path / "budget_workflow.db"
            if db_path.exists():
                shutil.copy2(db_path, self.backup_dir / "budget_workflow.db")
                self.log("✅ Base de données sauvegardée")
            
            # Sauvegarder les fichiers Python critiques
            critical_files = [
                "models/database.py",
                "models/demande.py", 
                "controllers/auth_controller.py",
                "services/workflow_service.py"
            ]
            
            for file_path in critical_files:
                src = self.project_path / file_path
                if src.exists():
                    dst = self.backup_dir / file_path
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    self.log(f"✅ {file_path} sauvegardé")
            
            self.log(f"🎉 Sauvegarde créée dans: {self.backup_dir}")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur sauvegarde: {e}", "ERROR")
            return False
    
    def create_permission_service(self):
        """Créer le nouveau PermissionService"""
        try:
            self.log("🔄 Création du PermissionService...")
            
            services_dir = self.project_path / "services"
            services_dir.mkdir(exist_ok=True)
            
            # Créer __init__.py si nécessaire
            init_file = services_dir / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")
            
            permission_service_code = '''"""
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
'''
            
            permission_file = services_dir / "permission_service.py"
            permission_file.write_text(permission_service_code)
            
            self.log("✅ PermissionService créé")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur création PermissionService: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def update_database_py(self):
        """Mettre à jour database.py avec les corrections"""
        try:
            self.log("🔄 Mise à jour de database.py...")
            
            database_code = '''"""
Database connection and initialization - Version Corrigée
"""
import sqlite3
import os
from contextlib import contextmanager
from typing import Optional, Any, Union, List
import logging
from config.settings import db_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Database:
    """Database connection manager - Version corrigée"""
    
    def __init__(self):
        self.use_sharepoint = False
        self.db_path = db_config.path
        logger.info("💾 Mode local activé")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with error handling"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Erreur connexion base de données: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None) -> Any:
        """Execute a query and return results with improved error handling"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
                
                if fetch == 'one':
                    return cursor.fetchone()
                elif fetch == 'all':
                    return cursor.fetchall()
                elif fetch == 'lastrowid':
                    conn.commit()
                    return cursor.lastrowid
                else:
                    conn.commit()
                    return cursor.rowcount
                    
        except sqlite3.IntegrityError as e:
            logger.error(f"Erreur d'intégrité: {e}")
            raise ValueError(f"Erreur d'intégrité de données: {e}")
        except sqlite3.Error as e:
            logger.error(f"Erreur SQLite: {e}")
            raise RuntimeError(f"Erreur base de données: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
            raise
    
    def table_exists(self, table_name: str) -> bool:
        """Vérifier si une table existe"""
        try:
            result = self.execute_query(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,),
                fetch='one'
            )
            return result is not None
        except Exception:
            return False
    
    def column_exists(self, table_name: str, column_name: str) -> bool:
        """Vérifier si une colonne existe dans une table"""
        try:
            result = self.execute_query(f"PRAGMA table_info({table_name})", fetch='all')
            if result:
                columns = [row[1] for row in result]
                return column_name in columns
            return False
        except Exception:
            return False
    
    def add_column_if_not_exists(self, table_name: str, column_name: str, column_def: str):
        """Ajouter une colonne si elle n'existe pas"""
        try:
            if not self.column_exists(table_name, column_name):
                self.execute_query(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_def}")
                logger.info(f"➕ Colonne {column_name} ajoutée à {table_name}")
        except Exception as e:
            logger.error(f"Erreur ajout colonne {column_name}: {e}")
    
    def init_database(self):
        """Initialize database with all tables - Version corrigée"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                logger.info("🚀 Initialisation de la base de données...")
                
                # TABLE USERS
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL,
                        nom TEXT NOT NULL,
                        prenom TEXT NOT NULL,
                        role TEXT NOT NULL CHECK (role IN ('admin', 'tc', 'dr', 'dr_financier', 'dg', 'marketing')),
                        region TEXT,
                        budget_alloue REAL DEFAULT 0,
                        directeur_id INTEGER,
                        is_active BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activated_at TIMESTAMP,
                        last_login TIMESTAMP,
                        FOREIGN KEY (directeur_id) REFERENCES users (id) ON DELETE SET NULL
                    )
                \'\'\')
                
                # TABLE DEMANDES
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS demandes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        type_demande TEXT NOT NULL CHECK (type_demande IN ('budget', 'marketing')),
                        nom_manifestation TEXT NOT NULL,
                        client TEXT NOT NULL,
                        date_evenement DATE NOT NULL,
                        lieu TEXT NOT NULL,
                        montant REAL NOT NULL CHECK (montant > 0),
                        participants TEXT DEFAULT '',
                        commentaires TEXT,
                        urgence TEXT DEFAULT 'normale' CHECK (urgence IN ('faible', 'normale', 'haute', 'critique')),
                        budget TEXT DEFAULT '',
                        categorie TEXT DEFAULT '',
                        typologie_client TEXT DEFAULT '',
                        groupe_groupement TEXT DEFAULT '',
                        region TEXT DEFAULT '',
                        agence TEXT DEFAULT '',
                        client_enseigne TEXT DEFAULT '',
                        mail_contact TEXT DEFAULT '',
                        nom_contact TEXT DEFAULT '',
                        demandeur_participe BOOLEAN DEFAULT TRUE,
                        participants_libres TEXT DEFAULT '',
                        cy INTEGER,
                        by TEXT,
                        status TEXT DEFAULT 'brouillon' CHECK (status IN ('brouillon', 'en_attente_dr', 'en_attente_financier', 'validee', 'rejetee')),
                        valideur_dr_id INTEGER,
                        valideur_financier_id INTEGER,
                        valideur_dg_id INTEGER,
                        date_validation_dr TIMESTAMP,
                        date_validation_financier TIMESTAMP,
                        date_validation_dg TIMESTAMP,
                        commentaire_dr TEXT,
                        commentaire_financier TEXT,
                        commentaire_dg TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (valideur_dr_id) REFERENCES users (id) ON DELETE SET NULL,
                        FOREIGN KEY (valideur_financier_id) REFERENCES users (id) ON DELETE SET NULL,
                        FOREIGN KEY (valideur_dg_id) REFERENCES users (id) ON DELETE SET NULL
                    )
                \'\'\')
                
                # TABLE DEMANDE_VALIDATIONS - MANQUANTE CRÉÉE
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS demande_validations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        demande_id INTEGER NOT NULL,
                        validated_by INTEGER NOT NULL,
                        validation_type TEXT NOT NULL CHECK (validation_type IN ('dr', 'financier', 'dg')),
                        action TEXT NOT NULL CHECK (action IN ('valider', 'rejeter')),
                        commentaire TEXT,
                        validated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (demande_id) REFERENCES demandes (id) ON DELETE CASCADE,
                        FOREIGN KEY (validated_by) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(demande_id, validated_by, validation_type)
                    )
                \'\'\')
                
                # TABLE DEMANDE_PARTICIPANTS
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS demande_participants (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        demande_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        added_by_user_id INTEGER NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (demande_id) REFERENCES demandes (id) ON DELETE CASCADE,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (added_by_user_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(demande_id, user_id)
                    )
                \'\'\')
                
                # TABLE NOTIFICATIONS
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS notifications (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        demande_id INTEGER,
                        type_notification TEXT NOT NULL,
                        titre TEXT NOT NULL,
                        message TEXT NOT NULL,
                        is_read BOOLEAN DEFAULT FALSE,
                        sent_by_email BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        read_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (demande_id) REFERENCES demandes (id) ON DELETE CASCADE
                    )
                \'\'\')
                
                # TABLE ACTIVITY_LOGS
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS activity_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        demande_id INTEGER,
                        action TEXT NOT NULL,
                        details TEXT,
                        ip_address TEXT,
                        user_agent TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        FOREIGN KEY (demande_id) REFERENCES demandes (id) ON DELETE SET NULL
                    )
                \'\'\')
                
                # TABLE DROPDOWN_OPTIONS
                cursor.execute(\'\'\'
                    CREATE TABLE IF NOT EXISTS dropdown_options (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        category TEXT NOT NULL,
                        value TEXT NOT NULL,
                        label TEXT NOT NULL,
                        order_index INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by INTEGER,
                        FOREIGN KEY (created_by) REFERENCES users (id) ON DELETE SET NULL,
                        UNIQUE(category, value)
                    )
                \'\'\')
                
                # Migrations et données par défaut
                self._run_migrations(cursor)
                self._create_default_data(cursor)
                self._create_indexes(cursor)
                
                conn.commit()
                logger.info("✅ Base de données initialisée avec succès")
                
        except Exception as e:
            logger.error(f"❌ Erreur initialisation base: {e}")
            raise
    
    def _run_migrations(self, cursor):
        """Exécuter les migrations nécessaires"""
        logger.info("🔄 Exécution des migrations...")
        try:
            self.add_column_if_not_exists('users', 'last_login', 'TIMESTAMP')
            self.add_column_if_not_exists('demandes', 'demandeur_participe', 'BOOLEAN DEFAULT TRUE')
            self.add_column_if_not_exists('demandes', 'participants_libres', 'TEXT DEFAULT ""')
            self.add_column_if_not_exists('demandes', 'cy', 'INTEGER')
            self.add_column_if_not_exists('demandes', 'by', 'TEXT')
            self.add_column_if_not_exists('demandes', 'valideur_dg_id', 'INTEGER')
            self.add_column_if_not_exists('demandes', 'date_validation_dg', 'TIMESTAMP')
            self.add_column_if_not_exists('demandes', 'commentaire_dg', 'TEXT')
            self.add_column_if_not_exists('notifications', 'sent_by_email', 'BOOLEAN DEFAULT FALSE')
            self.add_column_if_not_exists('notifications', 'read_at', 'TIMESTAMP')
            self.add_column_if_not_exists('activity_logs', 'ip_address', 'TEXT')
            self.add_column_if_not_exists('activity_logs', 'user_agent', 'TEXT')
            self.add_column_if_not_exists('dropdown_options', 'created_by', 'INTEGER')
            logger.info("✅ Migrations terminées")
        except Exception as e:
            logger.error(f"❌ Erreur migration: {e}")
            raise
    
    def _create_default_data(self, cursor):
        """Créer les données par défaut"""
        try:
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                from utils.security import hash_password
                admin_password = hash_password("admin123")
                cursor.execute(\'\'\'
                    INSERT INTO users (email, password_hash, nom, prenom, role, is_active, activated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                \'\'\', ("admin@budget.com", admin_password, "Administrateur", "Système", "admin", True))
                logger.info("👤 Administrateur par défaut créé")
            
            cursor.execute("SELECT COUNT(*) FROM dropdown_options")
            if cursor.fetchone()[0] == 0:
                self._init_dropdown_options(cursor)
                
        except Exception as e:
            logger.error(f"❌ Erreur création données par défaut: {e}")
            raise
    
    def _init_dropdown_options(self, cursor):
        """Initialiser les options de listes déroulantes"""
        default_options = [
            ('budget', 'budget_marketing', 'Budget Marketing', 1),
            ('budget', 'budget_commercial', 'Budget Commercial', 2),
            ('budget', 'budget_evenements', 'Budget Événements', 3),
            ('categorie', 'salon_foire', 'Salon / Foire', 1),
            ('categorie', 'conference', 'Conférence', 2),
            ('categorie', 'formation', 'Formation', 3),
            ('categorie', 'animation', 'Animation commerciale', 4),
            ('typologie_client', 'prospect', 'Prospect', 1),
            ('typologie_client', 'client_actuel', 'Client actuel', 2),
            ('typologie_client', 'client_vip', 'Client VIP', 3),
            ('typologie_client', 'partenaire', 'Partenaire', 4),
            ('groupe_groupement', 'grande_distribution', 'Grande Distribution', 1),
            ('groupe_groupement', 'commerce_independant', 'Commerce Indépendant', 2),
            ('groupe_groupement', 'entreprise', 'Entreprise', 4),
            ('region', 'ile_de_france', 'Île-de-France', 1),
            ('region', 'nord', 'Nord', 2),
            ('region', 'sud', 'Sud', 3),
            ('region', 'est', 'Est', 4),
            ('region', 'ouest', 'Ouest', 5),
        ]
        
        for category, value, label, order_index in default_options:
            cursor.execute(\'\'\'
                INSERT OR IGNORE INTO dropdown_options (category, value, label, order_index)
                VALUES (?, ?, ?, ?)
            \'\'\', (category, value, label, order_index))
        
        logger.info("📋 Options par défaut créées")
    
    def _create_indexes(self, cursor):
        """Créer les index pour optimiser les performances"""
        try:
            indexes = [
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_role ON users(role)",
                "CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active)",
                "CREATE INDEX IF NOT EXISTS idx_demandes_user ON demandes(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_demandes_status ON demandes(status)",
                "CREATE INDEX IF NOT EXISTS idx_demandes_type ON demandes(type_demande)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)",
                "CREATE INDEX IF NOT EXISTS idx_activity_user ON activity_logs(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_participants_demande ON demande_participants(demande_id)",
                "CREATE INDEX IF NOT EXISTS idx_validations_demande ON demande_validations(demande_id)",
                "CREATE INDEX IF NOT EXISTS idx_dropdown_category ON dropdown_options(category)",
            ]
            
            for index_query in indexes:
                cursor.execute(index_query)
            
            logger.info("🔍 Index créés pour optimiser les performances")
            
        except Exception as e:
            logger.error(f"❌ Erreur création index: {e}")
            raise

# Instance globale de la base de données
db = Database()
'''
            
            database_file = self.project_path / "models" / "database.py"
            database_file.write_text(database_code)
            
            self.log("✅ database.py mis à jour")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur mise à jour database.py: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def update_auth_controller(self):
        """Mettre à jour auth_controller.py"""
        try:
            self.log("🔄 Mise à jour du AuthController...")
            
            auth_controller_code = '''"""
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
        """Traiter une connexion réussie"""
        try:
            user_id = user_info['id']
            
            UserModel.update_user(user_id, last_login=datetime.now().isoformat())
            
            ActivityLogModel.log_activity(
                user_id, None, 'connexion',
                f"Connexion réussie pour {user_info['email']}"
            )
            
            st.session_state.logged_in = True
            st.session_state.user_id = user_id
            st.session_state.user_info = user_info
            st.session_state.page = "dashboard"
            
            logger.info(f"Connexion réussie: {user_info['email']} ({user_info['role']})")
            
        except Exception as e:
            logger.error(f"Erreur traitement connexion réussie: {e}")
    
    @staticmethod
    def logout(user_id: Optional[int] = None):
        """Déconnecter un utilisateur"""
        try:
            if user_id is None:
                user_id = st.session_state.get('user_id')
            
            if user_id:
                user_info = st.session_state.get('user_info', {})
                email = user_info.get('email', 'unknown')
                
                ActivityLogModel.log_activity(
                    user_id, None, 'deconnexion', f"Déconnexion de {email}"
                )
                
                logger.info(f"Déconnexion: {email}")
            
            AuthController._clear_session()
            
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")
            AuthController._clear_session()
    
    @staticmethod
    def _clear_session():
        """Nettoyer la session utilisateur"""
        try:
            keys_to_keep = set()
            keys_to_remove = []
            for key in st.session_state.keys():
                if key not in keys_to_keep:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del st.session_state[key]
            
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_info = {}
            st.session_state.page = "login"
            
        except Exception as e:
            logger.error(f"Erreur nettoyage session: {e}")
    
    @staticmethod
    def check_session() -> bool:
        """Vérifier la validité de la session utilisateur"""
        try:
            is_logged_in = st.session_state.get('logged_in', False)
            user_id = st.session_state.get('user_id')
            user_info = st.session_state.get('user_info', {})
            
            if not is_logged_in or not user_id or not user_info:
                return False
            
            user_data = UserModel.get_user_by_id(user_id)
            if not user_data or not user_data.get('is_active', False):
                logger.warning(f"Session invalide: utilisateur {user_id} inactif ou supprimé")
                AuthController._clear_session()
                return False
            
            if user_data != user_info:
                st.session_state.user_info = user_data
            
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
        """Obtenir l'utilisateur actuellement connecté"""
        if AuthController.check_session():
            return st.session_state.user_info
        return None
    
    @staticmethod
    def get_current_user_id() -> Optional[int]:
        """Obtenir l'ID de l'utilisateur actuellement connecté"""
        if AuthController.check_session():
            return st.session_state.user_id
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
'''
            
            auth_file = self.project_path / "controllers" / "auth_controller.py"
            auth_file.write_text(auth_controller_code)
            
            self.log("✅ AuthController mis à jour")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur mise à jour AuthController: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def run_database_migration(self):
        """Exécuter la migration de la base de données"""
        try:
            self.log("🔄 Migration de la base de données...")
            
            # Importer et initialiser la base
            sys.path.insert(0, str(self.project_path))
            from models.database import db
            
            # Lancer l'initialisation qui inclut les migrations
            db.init_database()
            
            # Vérifier que les nouvelles tables existent
            required_tables = [
                'users', 'demandes', 'demande_validations', 'demande_participants',
                'notifications', 'activity_logs', 'dropdown_options'
            ]
            
            missing_tables = []
            for table in required_tables:
                if not db.table_exists(table):
                    missing_tables.append(table)
            
            if missing_tables:
                self.log(f"❌ Tables manquantes: {missing_tables}", "ERROR")
                return False
            
            self.log("✅ Migration de la base réussie")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur migration base: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def test_corrections(self):
        """Tester les corrections appliquées"""
        try:
            self.log("🧪 Tests des corrections...")
            
            sys.path.insert(0, str(self.project_path))
            
            # Test 1: PermissionService
            try:
                from services.permission_service import permission_service, Permission
                
                # Test basique des permissions
                assert permission_service.has_permission('admin', Permission.CREATE_USER)
                assert permission_service.has_permission('tc', Permission.CREATE_DEMANDE)
                assert not permission_service.has_permission('tc', Permission.CREATE_USER)
                
                self.log("✅ Test PermissionService: OK")
                
            except Exception as e:
                self.log(f"❌ Test PermissionService échoué: {e}", "ERROR")
                return False
            
            # Test 2: Database
            try:
                from models.database import db
                
                # Test existence des tables
                assert db.table_exists('users')
                assert db.table_exists('demandes')
                assert db.table_exists('demande_validations')
                
                self.log("✅ Test Database: OK")
                
            except Exception as e:
                self.log(f"❌ Test Database échoué: {e}", "ERROR")
                return False
            
            # Test 3: AuthController
            try:
                from controllers.auth_controller import AuthController
                
                # Vérifier que les nouvelles méthodes existent
                assert hasattr(AuthController, 'has_permission')
                assert hasattr(AuthController, 'can_validate_demande')
                
                self.log("✅ Test AuthController: OK")
                
            except Exception as e:
                self.log(f"❌ Test AuthController échoué: {e}", "ERROR")
                return False
            
            self.log("🎉 Tous les tests réussis")
            self.success_count += 1
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur tests: {e}", "ERROR")
            self.error_count += 1
            return False
    
    def cleanup_old_files(self):
        """Nettoyer les anciens fichiers si nécessaire"""
        try:
            self.log("🧹 Nettoyage des fichiers temporaires...")
            
            # Fichiers à supprimer si ils existent
            temp_files = [
                self.project_path / "temp_migration.py",
                self.project_path / "old_database.py.bak",
            ]
            
            for temp_file in temp_files:
                if temp_file.exists():
                    temp_file.unlink()
                    self.log(f"🗑️ Supprimé: {temp_file.name}")
            
            self.log("✅ Nettoyage terminé")
            return True
            
        except Exception as e:
            self.log(f"❌ Erreur nettoyage: {e}", "ERROR")
            return False
    
    def generate_summary(self):
        """Générer un résumé des corrections appliquées"""
        self.log("\n" + "="*60)
        self.log("📊 RÉSUMÉ DES CORRECTIONS APPLIQUÉES")
        self.log("="*60)
        
        self.log(f"✅ Corrections réussies: {self.success_count}")
        self.log(f"❌ Erreurs rencontrées: {self.error_count}")
        
        if self.error_count == 0:
            self.log("\n🎉 TOUTES LES CORRECTIONS ONT ÉTÉ APPLIQUÉES AVEC SUCCÈS!")
            self.log("📋 Modifications apportées:")
            self.log("   • PermissionService créé (services/permission_service.py)")
            self.log("   • Database.py mis à jour avec nouvelles tables")
            self.log("   • AuthController.py corrigé")
            self.log("   • Migrations automatiques exécutées")
            self.log("   • Index de performance ajoutés")
            
            self.log("\n🚀 PROCHAINES ÉTAPES:")
            self.log("   1. Redémarrer l'application: streamlit run main.py")
            self.log("   2. Se connecter avec: admin@budget.com / admin123")
            self.log("   3. Tester les nouvelles fonctionnalités")
            self.log("   4. Créer de nouveaux utilisateurs si nécessaire")
            
        else:
            self.log("\n⚠️ CERTAINES CORRECTIONS ONT ÉCHOUÉ")
            self.log("📋 Actions recommandées:")
            self.log("   1. Vérifier les logs d'erreur ci-dessus")
            self.log("   2. Corriger manuellement les problèmes")
            self.log("   3. Relancer le script si nécessaire")
            self.log(f"   4. Restaurer depuis le backup: {self.backup_dir}")
        
        self.log("="*60)
    
    def run(self):
        """Exécuter toutes les corrections"""
        self.log("🚀 DÉBUT DE L'APPLICATION DES CORRECTIONS BUDGETMANAGE")
        self.log("="*60)
        
        # Étape 1: Sauvegarde
        if not self.create_backup():
            self.log("❌ Arrêt: Échec de la sauvegarde", "ERROR")
            return False
        
        # Étape 2: Créer PermissionService
        self.create_permission_service()
        
        # Étape 3: Mettre à jour Database.py
        self.update_database_py()
        
        # Étape 4: Mettre à jour AuthController
        self.update_auth_controller()
        
        # Étape 5: Migration base de données
        self.run_database_migration()
        
        # Étape 6: Tests
        self.test_corrections()
        
        # Étape 7: Nettoyage
        self.cleanup_old_files()
        
        # Étape 8: Résumé
        self.generate_summary()
        
        return self.error_count == 0

def main():
    """Fonction principale"""
    print("🎯 Script de Correction Automatique BudgetManage")
    print("=" * 50)
    
    # Vérifier qu'on est dans le bon dossier
    if not Path("main.py").exists():
        print("❌ ERREUR: main.py non trouvé")
        print("   Exécutez ce script depuis le dossier racine de BudgetManage")
        return False
    
    # Demander confirmation
    response = input("\n⚠️  Ce script va modifier votre projet BudgetManage.\n"
                    "   Une sauvegarde sera créée automatiquement.\n"
                    "   Continuer? (o/N): ")
    
    if response.lower() not in ['o', 'oui', 'y', 'yes']:
        print("❌ Opération annulée par l'utilisateur")
        return False
    
    # Lancer les corrections
    corrector = BudgetManageCorrector()
    success = corrector.run()
    
    if success:
        print("\n🎉 CORRECTIONS APPLIQUÉES AVEC SUCCÈS!")
        print("   Vous pouvez maintenant redémarrer votre application.")
    else:
        print("\n❌ CERTAINES CORRECTIONS ONT ÉCHOUÉ")
        print("   Consultez les logs ci-dessus pour plus de détails.")
    
    return success

if __name__ == "__main__":
    main()