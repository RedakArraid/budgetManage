"""
Script de migration pour ajouter la table demande_participants si elle n'existe pas
"""
from models.database import db

def migrate_participants_table():
    """Créer la table demande_participants si elle n'existe pas"""
    try:
        # Vérifier si la table existe
        table_exists = db.execute_query("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='demande_participants'
        """, fetch='one')
        
        if not table_exists:
            print("Création de la table demande_participants...")
            
            # Créer la table
            db.execute_query("""
                CREATE TABLE demande_participants (
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
            """)
            
            print("✅ Table demande_participants créée avec succès")
            
            # Créer des index pour optimiser les performances
            db.execute_query("""
                CREATE INDEX idx_demande_participants_demande_id ON demande_participants(demande_id)
            """)
            
            db.execute_query("""
                CREATE INDEX idx_demande_participants_user_id ON demande_participants(user_id)
            """)
            
            print("✅ Index créés pour la table demande_participants")
            
        else:
            print("ℹ️ Table demande_participants existe déjà")
            
        # Vérifier si les colonnes demandeur_participe et participants_libres existent dans la table demandes
        demandes_columns = db.execute_query("""
            PRAGMA table_info(demandes)
        """, fetch='all')
        
        column_names = [col['name'] for col in demandes_columns] if demandes_columns else []
        
        # Ajouter les colonnes manquantes
        if 'demandeur_participe' not in column_names:
            print("Ajout de la colonne demandeur_participe...")
            db.execute_query("""
                ALTER TABLE demandes 
                ADD COLUMN demandeur_participe BOOLEAN DEFAULT TRUE
            """)
            print("✅ Colonne demandeur_participe ajoutée")
        
        if 'participants_libres' not in column_names:
            print("Ajout de la colonne participants_libres...")
            db.execute_query("""
                ALTER TABLE demandes 
                ADD COLUMN participants_libres TEXT DEFAULT ''
            """)
            print("✅ Colonne participants_libres ajoutée")
            
        print("🎉 Migration des participants terminée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration: {e}")
        return False

def test_participants_system():
    """Tester le système de participants"""
    try:
        print("\n🧪 Test du système de participants...")
        
        # Test 1: Vérifier que la table existe et est accessible
        count = db.execute_query("""
            SELECT COUNT(*) FROM demande_participants
        """, fetch='one')[0]
        
        print(f"✅ Table demande_participants accessible - {count} enregistrement(s)")
        
        # Test 2: Vérifier les colonnes de la table demandes
        demande_test = db.execute_query("""
            SELECT demandeur_participe, participants_libres 
            FROM demandes 
            LIMIT 1
        """, fetch='one')
        
        print("✅ Colonnes demandeur_participe et participants_libres accessibles")
        
        print("🎉 Tous les tests réussis!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors des tests: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de la migration des participants...")
    
    if migrate_participants_table():
        test_participants_system()
    else:
        print("❌ Migration échouée")
