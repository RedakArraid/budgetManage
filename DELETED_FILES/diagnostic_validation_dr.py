"""
Script de diagnostic pour identifier le problème de validation des DR
"""
import sys
import os
sys.path.append('/Users/kader/Desktop/projet-en-cours/budgetmanage')

from models.database import db
from controllers.auth_controller import AuthController
from controllers.demande_controller import DemandeController
from models.demande import DemandeModel
import pandas as pd

def diagnostic_validation_dr():
    """Diagnostic complet du système de validation DR"""
    
    print("🔍 DIAGNOSTIC - PROBLÈME VALIDATION DR")
    print("=" * 50)
    
    # 1. Vérifier la structure de la base de données
    print("\n1. Structure base de données:")
    try:
        # Vérifier les tables
        tables = db.execute_query("""
            SELECT name FROM sqlite_master WHERE type='table'
            ORDER BY name
        """, fetch='all')
        
        print(f"   Tables disponibles: {[t['name'] for t in tables]}")
        
        # Vérifier la structure de la table demandes
        columns = db.execute_query("PRAGMA table_info(demandes)", fetch='all')
        print(f"   Colonnes demandes: {[c['name'] for c in columns]}")
        
        # Vérifier la structure de la table users
        user_columns = db.execute_query("PRAGMA table_info(users)", fetch='all')
        print(f"   Colonnes users: {[c['name'] for c in user_columns]}")
        
    except Exception as e:
        print(f"   ❌ Erreur structure DB: {e}")
    
    # 2. Vérifier les utilisateurs DR
    print("\n2. Utilisateurs DR:")
    try:
        drs = db.execute_query("""
            SELECT id, nom, prenom, email, region, is_active
            FROM users WHERE role = 'dr'
            ORDER BY nom, prenom
        """, fetch='all')
        
        print(f"   Nombre de DR: {len(drs)}")
        for dr in drs:
            status = "✅ Actif" if dr['is_active'] else "❌ Inactif"
            print(f"   - {dr['prenom']} {dr['nom']} (ID: {dr['id']}, Région: {dr['region']}) {status}")
            
    except Exception as e:
        print(f"   ❌ Erreur récupération DR: {e}")
    
    # 3. Vérifier les demandes en attente DR
    print("\n3. Demandes en attente DR:")
    try:
        demandes_attente_dr = db.execute_query("""
            SELECT d.id, d.nom_manifestation, d.client, d.montant, d.status, d.user_id,
                   u.nom as user_nom, u.prenom as user_prenom, u.role as user_role, 
                   u.directeur_id, u.region as user_region
            FROM demandes d
            JOIN users u ON d.user_id = u.id
            WHERE d.status = 'en_attente_dr'
            ORDER BY d.created_at DESC
        """, fetch='all')
        
        print(f"   Nombre de demandes en attente DR: {len(demandes_attente_dr)}")
        for demande in demandes_attente_dr:
            print(f"   - ID {demande['id']}: {demande['nom_manifestation']} - {demande['montant']:,.0f}€")
            print(f"     Demandeur: {demande['user_prenom']} {demande['user_nom']} ({demande['user_role']})")
            print(f"     Directeur ID: {demande['directeur_id']}, Région: {demande['user_region']}")
            
    except Exception as e:
        print(f"   ❌ Erreur récupération demandes attente DR: {e}")
    
    # 4. Tester la logique de récupération pour chaque DR
    print("\n4. Test récupération demandes par DR:")
    try:
        drs_actifs = db.execute_query("""
            SELECT id, nom, prenom, region
            FROM users WHERE role = 'dr' AND is_active = TRUE
        """, fetch='all')
        
        for dr in drs_actifs:
            print(f"\n   DR: {dr['prenom']} {dr['nom']} (ID: {dr['id']}, Région: {dr['region']})")
            
            # Test avec la méthode du contrôleur
            try:
                demandes_dr = DemandeController.get_demandes_for_user(
                    dr['id'], 'dr', status_filter='en_attente_dr'
                )
                print(f"     Méthode contrôleur: {len(demandes_dr)} demandes")
                
                if not demandes_dr.empty:
                    for idx, row in demandes_dr.iterrows():
                        print(f"       - {row['nom_manifestation']} (Status: {row['status']})")
                        
            except Exception as e:
                print(f"     ❌ Erreur méthode contrôleur: {e}")
            
            # Test avec requête directe
            try:
                demandes_directes = db.execute_query("""
                    SELECT d.id, d.nom_manifestation, d.status, d.user_id,
                           u.nom, u.prenom, u.directeur_id
                    FROM demandes d
                    JOIN users u ON d.user_id = u.id
                    WHERE d.status = 'en_attente_dr' 
                    AND (d.user_id = ? OR u.directeur_id = ?)
                """, (dr['id'], dr['id']), fetch='all')
                
                print(f"     Requête directe: {len(demandes_directes)} demandes")
                for demande in demandes_directes:
                    print(f"       - {demande['nom_manifestation']} (User: {demande['user_id']}, Dir: {demande['directeur_id']})")
                    
            except Exception as e:
                print(f"     ❌ Erreur requête directe: {e}")
    
    except Exception as e:
        print(f"   ❌ Erreur test DR: {e}")
    
    # 5. Vérifier la relation directeur-équipe
    print("\n5. Relations Directeur-Équipe:")
    try:
        relations = db.execute_query("""
            SELECT tc.id as tc_id, tc.nom as tc_nom, tc.prenom as tc_prenom,
                   tc.directeur_id, dr.nom as dr_nom, dr.prenom as dr_prenom
            FROM users tc
            LEFT JOIN users dr ON tc.directeur_id = dr.id
            WHERE tc.role = 'tc' AND tc.is_active = TRUE
            ORDER BY dr.nom, tc.nom
        """, fetch='all')
        
        print(f"   Relations trouvées: {len(relations)}")
        for rel in relations:
            if rel['directeur_id']:
                print(f"   - TC {rel['tc_prenom']} {rel['tc_nom']} -> DR {rel['dr_prenom']} {rel['dr_nom']}")
            else:
                print(f"   - TC {rel['tc_prenom']} {rel['tc_nom']} -> ❌ Aucun directeur assigné")
                
    except Exception as e:
        print(f"   ❌ Erreur relations: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 FIN DU DIAGNOSTIC")

if __name__ == "__main__":
    # Initialiser la base de données
    db.init_database()
    diagnostic_validation_dr()
