"""
Utilitaire pour exécuter les migrations de base de données
"""
import sys
import os

# Ajouter le répertoire parent au chemin pour les imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_migrations():
    """Exécuter toutes les migrations disponibles"""
    try:
        print("🔄 Exécution des migrations de base de données...")
        
        # Migration des participants
        from migrations.migrate_participants import migrate_participants_table, test_participants_system
        
        print("\n📊 Migration des participants...")
        if migrate_participants_table():
            print("✅ Migration des participants terminée")
            test_participants_system()
        else:
            print("❌ Échec de la migration des participants")
            return False
        
        # Migration des valeurs dropdown
        from migrations.update_dropdown_values import update_dropdown_values
        
        print("\n🎛️ Migration des valeurs des listes déroulantes...")
        if update_dropdown_values():
            print("✅ Migration des valeurs dropdown terminée")
        else:
            print("❌ Échec de la migration des valeurs dropdown")
            return False
        
        print("\n🎉 Toutes les migrations ont été exécutées avec succès!")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution des migrations: {e}")
        return False

if __name__ == "__main__":
    run_migrations()
