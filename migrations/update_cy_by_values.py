"""
Script pour mettre à jour les demandes existantes avec les valeurs cy et by
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.database import db
from models.demande import calculate_cy_by

def update_existing_demandes():
    """Met à jour toutes les demandes existantes avec cy et by"""
    try:
        # Récupérer toutes les demandes sans cy/by
        demandes = db.execute_query('''
            SELECT id, date_evenement FROM demandes 
            WHERE cy IS NULL OR by IS NULL
        ''', fetch='all')
        
        if not demandes:
            print("✅ Aucune demande à mettre à jour")
            return
        
        print(f"🔄 Mise à jour de {len(demandes)} demandes...")
        
        updated_count = 0
        for demande in demandes:
            demande_id = demande['id']
            date_evenement = demande['date_evenement']
            
            # Calculer cy et by
            cy, by = calculate_cy_by(date_evenement)
            
            if cy and by:
                # Mettre à jour la demande
                db.execute_query('''
                    UPDATE demandes 
                    SET cy = ?, by = ? 
                    WHERE id = ?
                ''', (cy, by, demande_id))
                updated_count += 1
                print(f"  ✓ Demande {demande_id}: {date_evenement} → cy={cy}, by={by}")
        
        print(f"✅ {updated_count} demandes mises à jour avec succès")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour: {e}")

if __name__ == "__main__":
    update_existing_demandes()
