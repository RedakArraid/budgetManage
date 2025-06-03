"""
Migration pour ajouter les champs cy (année civile) et by (année fiscale)
"""
import sqlite3
from datetime import datetime
from models.database import db

def calculate_cy_by(date_evenement):
    """
    Calculer cy (année civile) et by (année fiscale) à partir de la date d'événement
    L'année fiscale commence en mai
    """
    if not date_evenement:
        return None, None
    
    # Convertir en datetime si c'est une string
    if isinstance(date_evenement, str):
        try:
            date_obj = datetime.strptime(date_evenement, '%Y-%m-%d').date()
        except ValueError:
            try:
                date_obj = datetime.strptime(date_evenement, '%d/%m/%Y').date()
            except ValueError:
                return None, None
    else:
        date_obj = date_evenement
    
    # cy = année civile (simple)
    cy = date_obj.year
    
    # by = année fiscale (commence en mai)
    if date_obj.month >= 5:  # Mai à décembre
        # Année fiscale actuelle : ex 2024/25
        by_start = cy
        by_end = cy + 1
    else:  # Janvier à avril
        # Année fiscale précédente : ex 23/24
        by_start = cy - 1
        by_end = cy
    
    # Format : YY/YY (ex: 23/24, 24/25)
    by = f"{str(by_start)[2:]}/{str(by_end)[2:]}"
    
    return cy, by

def run_migration():
    """Exécuter la migration pour ajouter cy et by"""
    try:
        with db.get_connection() as conn:
            cursor = conn.cursor()
            
            # Vérifier si les colonnes existent déjà
            cursor.execute("PRAGMA table_info(demandes)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # Ajouter la colonne cy si elle n'existe pas
            if 'cy' not in columns:
                cursor.execute("ALTER TABLE demandes ADD COLUMN cy INTEGER")
                print("➕ Colonne cy (année civile) ajoutée")
            
            # Ajouter la colonne by si elle n'existe pas
            if 'by' not in columns:
                cursor.execute("ALTER TABLE demandes ADD COLUMN by TEXT")
                print("➕ Colonne by (année fiscale) ajoutée")
            
            # Mettre à jour toutes les demandes existantes avec les valeurs calculées
            cursor.execute("SELECT id, date_evenement FROM demandes WHERE date_evenement IS NOT NULL")
            demandes = cursor.fetchall()
            
            updated_count = 0
            for demande in demandes:
                demande_id = demande['id']
                date_evenement = demande['date_evenement']
                
                cy, by = calculate_cy_by(date_evenement)
                
                if cy and by:
                    cursor.execute(
                        "UPDATE demandes SET cy = ?, by = ? WHERE id = ?",
                        (cy, by, demande_id)
                    )
                    updated_count += 1
            
            conn.commit()
            print(f"✅ {updated_count} demandes mises à jour avec cy/by")
            print("Migration cy/by terminée avec succès")
            
    except Exception as e:
        print(f"❌ Erreur lors de la migration cy/by: {e}")
        raise

if __name__ == "__main__":
    run_migration()
