#!/usr/bin/env python3
"""
Script pour tester et corriger le problème de stats dashboard
"""
import sys
import os

# Ajouter le répertoire racine au path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.database import db
from models.demande import DemandeModel
from models.user import UserModel

def test_dashboard_stats():
    """Test des statistiques dashboard pour différents rôles"""
    
    print("🧪 Test des statistiques dashboard...")
    
    # Initialiser la base de données
    db.init_database()
    
    # Récupérer des utilisateurs de test
    users = db.execute_query(
        "SELECT id, email, role FROM users LIMIT 5", 
        fetch='all'
    )
    
    if not users:
        print("❌ Aucun utilisateur trouvé dans la base de données")
        return
    
    for user in users:
        user_id = user['id']
        role = user['role']
        email = user['email']
        
        print(f"\n👤 Test pour utilisateur: {email} (ID: {user_id}, Rôle: {role})")
        
        try:
            # Tester les stats sans année fiscale
            stats = DemandeModel.get_dashboard_stats(user_id, role)
            print(f"✅ Stats sans année fiscale: {stats}")
            
            # Vérifier que montant_valide n'est pas None
            montant_valide = stats.get('montant_valide')
            if montant_valide is None:
                print(f"❌ montant_valide est None pour {email}")
            else:
                print(f"✅ montant_valide = {montant_valide:,.0f}€")
            
            # Tester les stats avec année fiscale 2024
            stats_2024 = DemandeModel.get_dashboard_stats(user_id, role, fiscal_year=2024)
            print(f"✅ Stats pour 2024: {stats_2024}")
            
        except Exception as e:
            print(f"❌ Erreur pour {email}: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
    
    print("\n🎯 Test de formatage des montants...")
    
    # Test des cas limites
    test_values = [None, 0, 1234.56, 1000000]
    
    for value in test_values:
        try:
            formatted = f"{(value or 0):,.0f}€"
            print(f"✅ {value} → {formatted}")
        except Exception as e:
            print(f"❌ Erreur formatage {value}: {e}")

def create_test_data():
    """Créer des données de test pour vérifier les stats"""
    
    print("📊 Création de données de test...")
    
    try:
        # Récupérer un utilisateur TC
        tc_user = db.execute_query(
            "SELECT id FROM users WHERE role = 'tc' AND is_active = TRUE LIMIT 1",
            fetch='one'
        )
        
        if not tc_user:
            print("❌ Aucun utilisateur TC trouvé")
            return
        
        user_id = tc_user['id']
        
        # Créer une demande de test
        from datetime import datetime, date
        
        success, demande_id = DemandeModel.create_demande(
            user_id=user_id,
            type_demande='budget',
            nom_manifestation='Test Manifestation',
            client='Client Test',
            date_evenement='2024-12-15',
            lieu='Paris',
            montant=5000.0,
            commentaires='Test pour dashboard stats',
            fy=2024,
            by='BY24'
        )
        
        if success:
            print(f"✅ Demande de test créée (ID: {demande_id})")
            
            # Valider la demande pour avoir un montant_valide > 0
            DemandeModel.update_demande(
                demande_id,
                status='validee',
                valideur_dr_id=user_id,
                valideur_financier_id=user_id,
                date_validation_dr=datetime.now().isoformat(),
                date_validation_financier=datetime.now().isoformat(),
                commentaire_dr='Test validation',
                commentaire_financier='Test validation'
            )
            
            print(f"✅ Demande validée pour test")
            
        else:
            print("❌ Erreur création demande de test")
    
    except Exception as e:
        print(f"❌ Erreur création données test: {e}")

if __name__ == "__main__":
    print("🚀 Script de test dashboard stats")
    print("=" * 50)
    
    # Créer des données de test
    create_test_data()
    
    # Tester les stats
    test_dashboard_stats()
    
    print("\n✅ Test terminé")
