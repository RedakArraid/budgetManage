"""
Système simplifié pour les dropdown - stockage direct des valeurs métier
Plus besoin de mapping complexe, la valeur stockée = la valeur affichée
"""

from models.dropdown_options import DropdownOptionsModel
from typing import List, Dict

class SimpleDropdownManager:
    """Gestionnaire simplifié pour les dropdown - valeur stockée = valeur affichée"""
    
    @staticmethod
    def get_options_for_selectbox(category: str) -> List[str]:
        """
        Récupère les options pour un selectbox Streamlit
        Retourne directement les valeurs (qui sont aussi les labels)
        """
        try:
            options = DropdownOptionsModel.get_options_for_category(category)
            # Maintenant value = label, donc on retourne juste les values
            return [opt['value'] for opt in options]
        except Exception as e:
            print(f"Erreur récupération options {category}: {e}")
            return []
    
    @staticmethod
    def add_option_simple(category: str, value_label: str) -> tuple[bool, str]:
        """
        Ajoute une option où value = label
        Ex: add_option_simple('budget', 'SALES') stocke value='SALES', label='SALES'
        """
        try:
            return DropdownOptionsModel.add_option(category, value_label, value_label)
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def get_all_current_values() -> Dict[str, List[str]]:
        """Récupère toutes les valeurs actuellement utilisées dans les demandes"""
        from models.database import db
        
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        current_values = {}
        
        for category in categories:
            values = db.execute_query(f'''
                SELECT DISTINCT {category}
                FROM demandes 
                WHERE {category} IS NOT NULL AND {category} != ''
                ORDER BY {category}
            ''', fetch='all')
            
            current_values[category] = [row[0] for row in values] if values else []
        
        return current_values
    
    @staticmethod
    def ensure_all_used_values_have_options():
        """S'assure que toutes les valeurs utilisées dans les demandes ont des options"""
        current_values = SimpleDropdownManager.get_all_current_values()
        created_count = 0
        
        for category, values in current_values.items():
            for value in values:
                # Vérifier si l'option existe
                from models.database import db
                existing = db.execute_query('''
                    SELECT id FROM dropdown_options
                    WHERE category = ? AND value = ? AND is_active = TRUE
                ''', (category, value), fetch='one')
                
                if not existing:
                    # Créer l'option manquante
                    success, message = SimpleDropdownManager.add_option_simple(category, value)
                    if success:
                        print(f"✅ Option créée: {category}.{value}")
                        created_count += 1
                    else:
                        print(f"❌ Erreur création {category}.{value}: {message}")
        
        return created_count

def migrate_to_simple_system():
    """Migre vers le système simplifié value=label"""
    print("🔄 Migration vers le système simplifié...")
    
    # S'assurer que toutes les valeurs utilisées ont des options
    created = SimpleDropdownManager.ensure_all_used_values_have_options()
    print(f"📊 {created} options créées pour les valeurs manquantes")
    
    # Vider le cache
    from utils.dropdown_display import DropdownDisplayUtils
    DropdownDisplayUtils.clear_cache()
    
    print("✅ Migration vers le système simplifié terminée")
    print("💡 Maintenant: valeur stockée = valeur affichée (plus de mapping)")

if __name__ == "__main__":
    migrate_to_simple_system()
