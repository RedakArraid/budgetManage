"""
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
            else:
                logger.info(f"✅ Colonne {column_name} existe déjà dans {table_name}")
        except Exception as e:
            logger.error(f"Erreur ajout colonne {column_name}: {e}")
    
    def init_database(self):
        """Initialize database with all tables - Version corrigée"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                logger.info("🚀 Initialisation de la base de données...")
                
                # TABLE USERS
                cursor.execute('''
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
                ''')
                
                # TABLE USER_BUDGETS - NOUVELLE TABLE
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS user_budgets (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        fiscal_year INTEGER NOT NULL,
                        allocated_budget REAL NOT NULL DEFAULT 0.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                        UNIQUE(user_id, fiscal_year)
                    )
                ''')
                
                # TABLE DEMANDES
                cursor.execute('''
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
                ''')
                
                # Add fiscal_year column if it doesn't exist
                self.add_column_if_not_exists('demandes', 'fiscal_year', "INTEGER NOT NULL DEFAULT (CAST(strftime('%Y', CURRENT_TIMESTAMP) AS INTEGER))")
                
                # TABLE DEMANDE_VALIDATIONS - MANQUANTE CRÉÉE
                cursor.execute('''
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
                ''')
                
                # TABLE DEMANDE_PARTICIPANTS
                cursor.execute('''
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
                ''')
                
                # TABLE NOTIFICATIONS
                cursor.execute('''
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
                ''')
                
                # TABLE ACTIVITY_LOGS
                cursor.execute('''
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
                ''')
                
                # TABLE DROPDOWN_OPTIONS
                cursor.execute('''
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
                ''')
                
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
            self.add_column_if_not_exists('demandes', 'fiscal_year', 'INTEGER')
            self.add_column_if_not_exists('demandes', 'valideur_dg_id', 'INTEGER')
            self.add_column_if_not_exists('demandes', 'date_validation_dg', 'TIMESTAMP')
            self.add_column_if_not_exists('demandes', 'commentaire_dg', 'TEXT')
            self.add_column_if_not_exists('notifications', 'sent_by_email', 'BOOLEAN DEFAULT FALSE')
            self.add_column_if_not_exists('notifications', 'read_at', 'TIMESTAMP')
            self.add_column_if_not_exists('activity_logs', 'ip_address', 'TEXT')
            self.add_column_if_not_exists('activity_logs', 'user_agent', 'TEXT')
            self.add_column_if_not_exists('dropdown_options', 'created_by', 'INTEGER')
            logger.info("✅ Migrations terminées")
            
            # Migration to remove old budget_alloue column from users table
            if self.column_exists('users', 'budget_alloue'):
                # SQLite does not support dropping columns directly in older versions
                # The standard approach is to: rename table, create new table, copy data, drop old table
                # However, for simplicity and assuming a recent enough SQLite or accepting potential data loss for this single column,
                # we can attempt to drop the column. If it fails, a manual step might be needed.
                try:
                    self.execute_query("ALTER TABLE users DROP COLUMN budget_alloue")
                    logger.info("🗑️ Colonne budget_alloue supprimée de la table users")
                except Exception as e:
                    logger.warning(f"⚠️ Impossible de supprimer la colonne budget_alloue de la table users: {e}. Une migration manuelle peut être nécessaire.")

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
                cursor.execute('''
                    INSERT INTO users (email, password_hash, nom, prenom, role, is_active, activated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', ("admin@budget.com", admin_password, "Administrateur", "Système", "admin", True))
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
            # Années fiscales
            ('annee_fiscale', '2020', 'BY20', 1),
            ('annee_fiscale', '2021', 'BY21', 2),
            ('annee_fiscale', '2022', 'BY22', 3),
            ('annee_fiscale', '2023', 'BY23', 4),
            ('annee_fiscale', '2024', 'BY24', 5),
            ('annee_fiscale', '2025', 'BY25', 6),
            ('annee_fiscale', '2026', 'BY26', 7),
            ('annee_fiscale', '2027', 'BY27', 8),
            ('annee_fiscale', '2028', 'BY28', 9),
            ('annee_fiscale', '2029', 'BY29', 10),
            ('annee_fiscale', '2030', 'BY30', 11),
        ]
        
        for category, value, label, order_index in default_options:
            cursor.execute('''
                INSERT OR IGNORE INTO dropdown_options (category, value, label, order_index)
                VALUES (?, ?, ?, ?)
            ''', (category, value, label, order_index))
        
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
