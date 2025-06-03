"""
Diagnostic simple pour identifier le problème de validation DR
"""
import sys
import sqlite3
import os

# Chemin vers la base de données
db_path = '/Users/kader/Desktop/projet-en-cours/budgetmanage/budget_workflow.db'

print("🔍 DIAGNOSTIC VALIDATION DR")
print("=" * 50)

try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Vérifier les demandes en attente DR
    print("\n1. Demandes en attente DR:")
    cursor.execute("""
        SELECT d.id, d.nom_manifestation, d.status, d.user_id,
               u.nom, u.prenom, u.role, u.directeur_id
        FROM demandes d
        JOIN users u ON d.user_id = u.id
        WHERE d.status = 'en_attente_dr'
    """)
    demandes = cursor.fetchall()
    
    print(f"   Nombre total: {len(demandes)}")
    for demande in demandes:
        print(f"   - {demande['nom_manifestation']} (ID: {demande['id']})")
        print(f"     Créateur: {demande['prenom']} {demande['nom']} (Role: {demande['role']}, Directeur: {demande['directeur_id']})")
    
    # 2. Vérifier les DR actifs
    print("\n2. DR actifs:")
    cursor.execute("""
        SELECT id, nom, prenom, region, is_active
        FROM users WHERE role = 'dr' AND is_active = 1
    """)
    drs = cursor.fetchall()
    
    print(f"   Nombre de DR: {len(drs)}")
    for dr in drs:
        print(f"   - {dr['prenom']} {dr['nom']} (ID: {dr['id']}, Région: {dr['region']})")
    
    # 3. Tester pour chaque DR quelles demandes il peut voir
    print("\n3. Test pour chaque DR:")
    for dr in drs:
        print(f"\n   DR: {dr['prenom']} {dr['nom']} (ID: {dr['id']})")
        
        # Requête pour voir les demandes que ce DR peut valider
        cursor.execute("""
            SELECT d.id, d.nom_manifestation, d.status, d.user_id,
                   u.nom, u.prenom, u.directeur_id
            FROM demandes d
            JOIN users u ON d.user_id = u.id
            WHERE d.status = 'en_attente_dr' 
            AND (d.user_id = ? OR u.directeur_id = ?)
        """, (dr['id'], dr['id']))
        
        demandes_dr = cursor.fetchall()
        print(f"     Peut valider: {len(demandes_dr)} demandes")
        
        for demande in demandes_dr:
            print(f"       - {demande['nom_manifestation']} (Creator: {demande['user_id']}, Dir: {demande['directeur_id']})")
    
    # 4. Relations directeur-équipe
    print("\n4. Relations TC-DR:")
    cursor.execute("""
        SELECT tc.id, tc.nom, tc.prenom, tc.directeur_id,
               dr.nom as dr_nom, dr.prenom as dr_prenom
        FROM users tc
        LEFT JOIN users dr ON tc.directeur_id = dr.id
        WHERE tc.role = 'tc' AND tc.is_active = 1
    """)
    relations = cursor.fetchall()
    
    for rel in relations:
        if rel['directeur_id']:
            print(f"   - TC {rel['prenom']} {rel['nom']} -> DR {rel['dr_prenom']} {rel['dr_nom']}")
        else:
            print(f"   - TC {rel['prenom']} {rel['nom']} -> ❌ Pas de directeur")
    
    conn.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("🏁 FIN DU DIAGNOSTIC")
