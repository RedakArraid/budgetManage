"""
Database connection and initialization - Compatible SharePoint et Local
"""
import sqlite3
import os
from contextlib import contextmanager
from config.settings import db_config

class Database:
    """Database connection manager compatible SharePoint et local"""
    
    def __init__(self):
        # FORCE MODE LOCAL UNIQUEMENT
        self.use_sharepoint = False
        self.db_path = db_config.path
        print("ℹ️ Mode local forcé")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        # MODE LOCAL UNIQUEMENT
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = None, fetch: str = None):
        """Execute a query and return results"""
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
    
    def init_database(self):
        """Initialize database with all tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des utilisateurs avec rôles et hiérarchie
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
                    FOREIGN KEY (directeur_id) REFERENCES users (id)
                )
            ''')
            
            # Table des demandes avec workflow
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demandes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    type_demande TEXT NOT NULL CHECK (type_demande IN ('budget', 'marketing')),
                    nom_manifestation TEXT NOT NULL,
                    client TEXT NOT NULL,
                    date_evenement DATE NOT NULL,
                    lieu TEXT NOT NULL,
                    montant REAL NOT NULL,
                    participants TEXT DEFAULT '',
                    commentaires TEXT,
                    urgence TEXT DEFAULT 'normale',
                    budget TEXT DEFAULT '',
                    categorie TEXT DEFAULT '',
                    typologie_client TEXT DEFAULT '',
                    groupe_groupement TEXT DEFAULT '',
                    region TEXT DEFAULT '',
                    agence TEXT DEFAULT '',
                    client_enseigne TEXT DEFAULT '',
                    mail_contact TEXT DEFAULT '',
                    nom_contact TEXT DEFAULT '',
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
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (valideur_dr_id) REFERENCES users (id),
                    FOREIGN KEY (valideur_financier_id) REFERENCES users (id),
                    FOREIGN KEY (valideur_dg_id) REFERENCES users (id)
                )
            ''')
            
            # Table des notifications
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    demande_id INTEGER,
                    type_notification TEXT NOT NULL,
                    titre TEXT NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (demande_id) REFERENCES demandes (id)
                )
            ''')
            
            # Table des logs d'activité
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    demande_id INTEGER,
                    action TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (demande_id) REFERENCES demandes (id)
                )
            ''')
            
            # Table des paramètres des listes déroulantes
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
                    UNIQUE(category, value)
                )
            ''')
            
            # Ajouter les colonnes DG si elles n'existent pas (migration)
            try:
                cursor.execute("PRAGMA table_info(demandes)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'valideur_dg_id' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN valideur_dg_id INTEGER")
                    print("➕ Colonne valideur_dg_id ajoutée")
                if 'date_validation_dg' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN date_validation_dg TIMESTAMP")
                    print("➕ Colonne date_validation_dg ajoutée")
                if 'commentaire_dg' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN commentaire_dg TEXT")
                    print("➕ Colonne commentaire_dg ajoutée")
                # Migration participants
                if 'demandeur_participe' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN demandeur_participe BOOLEAN DEFAULT TRUE")
                    print("➥ Colonne demandeur_participe ajoutée")
                if 'participants_libres' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN participants_libres TEXT DEFAULT ''")
                    print("➥ Colonne participants_libres ajoutée")
                # Migration cy/by (années civile et fiscale)
                if 'cy' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN cy INTEGER")
                    print("➥ Colonne cy (année civile) ajoutée")
                if 'by' not in columns:
                    cursor.execute("ALTER TABLE demandes ADD COLUMN by TEXT")
                    print("➥ Colonne by (année fiscale) ajoutée")
                    
            except Exception as e:
                print(f"⚠️ Migration colonnes: {e}")
            
            # Créer la table des participants si elle n'existe pas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS demande_participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    demande_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    added_by_user_id INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (demande_id) REFERENCES demandes (id) ON DELETE CASCADE,
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (added_by_user_id) REFERENCES users (id),
                    UNIQUE(demande_id, user_id)
                )
            ''')
            print("✅ Table demande_participants créée")
            
            # Créer un admin par défaut s'il n'existe pas
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
            if cursor.fetchone()[0] == 0:
                from utils.security import hash_password
                admin_password = hash_password("admin123")
                cursor.execute('''
                    INSERT INTO users (email, password_hash, nom, prenom, role, is_active)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', ("admin@budget.com", admin_password, "Administrateur", "Système", "admin", True))
                print("👤 Administrateur par défaut créé (admin@budget.com / admin123)")
            
            # Initialiser les listes déroulantes par défaut SEULEMENT si aucune option n'existe
            cursor.execute("SELECT COUNT(*) FROM dropdown_options")
            if cursor.fetchone()[0] == 0:
                print("📋 Initialisation des listes déroulantes par défaut...")
                print("⚠️ ATTENTION: Utilisez l'interface admin pour gérer les options après l'initialisation")
                
                default_options = [
                    # Budget
                    ('budget', 'budget_marketing', 'Budget Marketing', 1),
                    ('budget', 'budget_commercial', 'Budget Commercial', 2),
                    ('budget', 'budget_evenements', 'Budget Événements', 3),
                    
                    # Catégorie
                    ('categorie', 'salon_foire', 'Salon / Foire', 1),
                    ('categorie', 'conference', 'Conférence', 2),
                    ('categorie', 'formation', 'Formation', 3),
                    ('categorie', 'animation', 'Animation commerciale', 4),
                    
                    # Typologie Client
                    ('typologie_client', 'prospect', 'Prospect', 1),
                    ('typologie_client', 'client_actuel', 'Client actuel', 2),
                    ('typologie_client', 'client_vip', 'Client VIP', 3),
                    ('typologie_client', 'partenaire', 'Partenaire', 4),
                    
                    # Groupe/Groupement
                    ('groupe_groupement', 'grande_distribution', 'Grande Distribution', 1),
                    ('groupe_groupement', 'commerce_independant', 'Commerce Indépendant', 2),
                    ('groupe_groupement', 'collectivite', 'Collectivité', 3),
                    ('groupe_groupement', 'entreprise', 'Entreprise', 4),
                    
                    # Région
                    ('region', 'ile_de_france', 'Île-de-France', 1),
                    ('region', 'nord', 'Nord', 2),
                    ('region', 'sud', 'Sud', 3),
                    ('region', 'est', 'Est', 4),
                    ('region', 'ouest', 'Ouest', 5),
                ]
                
                for category, value, label, order_index in default_options:
                    cursor.execute('''
                        INSERT INTO dropdown_options (category, value, label, order_index)
                        VALUES (?, ?, ?, ?)
                    ''', (category, value, label, order_index))
                
                print("📋 Options par défaut créées - Utilisez l'interface admin pour les gérer")
            else:
                print("✅ Options déjà présentes - Utilisation des options existantes")
            
            conn.commit()
            print("✅ Base de données initialisée")

# Global database instance
db = Database()
