"""
Système centralisé de gestion des listes déroulantes
La page admin fait FOI - aucune valeur ne peut être stockée sans être définie d'abord
"""

import re
from typing import Optional, List, Dict, Tuple
from models.database import db
from models.dropdown_options import DropdownOptionsModel

class DropdownCentralManager:
    """Gestionnaire centralisé - La page admin contrôle tout"""
    
    @staticmethod
    def normalize_label_to_value(label: str) -> str:
        """
        Convertit un label en valeur stockable selon la règle :
        - Minuscule
        - Espaces remplacés par _
        - Caractères spéciaux nettoyés
        
        Ex: "NORD EST" → "nord_est"
        Ex: "Animation Client" → "animation_client"
        """
        if not label:
            return ""
        
        # Convertir en minuscules
        normalized = label.lower().strip()
        
        # Remplacer espaces et caractères spéciaux par _
        normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
        
        # Nettoyer les _ en début/fin et multiples
        normalized = re.sub(r'^_+|_+$', '', normalized)
        normalized = re.sub(r'_+', '_', normalized)
        
        return normalized
    
    @staticmethod
    def create_option_from_admin(category: str, label: str, order_index: int = None) -> Tuple[bool, str]:
        """
        Crée une option depuis la page admin
        C'est la SEULE façon de créer des options valides
        """
        try:
            if not label.strip():
                return False, "Le label ne peut pas être vide"
            
            # Générer la valeur normalisée
            value = DropdownCentralManager.normalize_label_to_value(label)
            
            if not value:
                return False, "Impossible de générer une valeur valide à partir du label"
            
            # Vérifier que cette valeur n'existe pas déjà
            existing = db.execute_query('''
                SELECT id FROM dropdown_options
                WHERE category = ? AND value = ?
            ''', (category, value), fetch='one')
            
            if existing:
                return False, f"Une option avec la valeur '{value}' existe déjà"
            
            # Déterminer l'ordre si non spécifié
            if order_index is None:
                max_order = db.execute_query('''
                    SELECT COALESCE(MAX(order_index), 0) FROM dropdown_options
                    WHERE category = ?
                ''', (category,), fetch='one')[0]
                order_index = max_order + 1
            
            # Créer l'option
            success, message = DropdownOptionsModel.add_option(category, value, label, order_index)
            
            if success:
                print(f"✅ Option créée: {category}.{value} = '{label}'")
                return True, f"Option créée: {value}"
            else:
                return False, message
                
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def validate_value_exists(category: str, value: str) -> bool:
        """
        Valide qu'une valeur existe dans les options actives
        OBLIGATOIRE avant tout stockage en base
        """
        try:
            option = db.execute_query('''
                SELECT id FROM dropdown_options
                WHERE category = ? AND value = ? AND is_active = TRUE
            ''', (category, value), fetch='one')
            
            return option is not None
            
        except Exception:
            return False
    
    @staticmethod
    def validate_demande_data(demande_data: Dict) -> Tuple[bool, List[str]]:
        """
        Valide toutes les valeurs dropdown d'une demande
        OBLIGATOIRE avant insertion/mise à jour
        """
        errors = []
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        
        for category in categories:
            value = demande_data.get(category)
            if value:  # Si une valeur est fournie
                if not DropdownCentralManager.validate_value_exists(category, value):
                    errors.append(f"Valeur '{value}' non autorisée pour {category}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_valid_options_for_form(category: str) -> List[Dict[str, str]]:
        """
        Récupère les options valides pour un formulaire
        SEULES ces options peuvent être utilisées
        """
        try:
            options = DropdownOptionsModel.get_options_for_category(category)
            
            # Format pour Streamlit : [{'value': 'nord_est', 'label': 'NORD EST'}, ...]
            return [
                {
                    'value': opt['value'],
                    'label': opt['label']
                }
                for opt in options
            ]
            
        except Exception as e:
            print(f"Erreur récupération options {category}: {e}")
            return []
    
    @staticmethod
    def get_display_label(category: str, stored_value: str) -> str:
        """
        Récupère le label d'affichage pour une valeur stockée
        """
        try:
            if not stored_value:
                return "Non spécifié"
            
            option = db.execute_query('''
                SELECT label FROM dropdown_options
                WHERE category = ? AND value = ? AND is_active = TRUE
            ''', (category, stored_value), fetch='one')
            
            if option:
                return option['label']
            else:
                # Valeur orpheline - ne devrait pas arriver avec la validation
                return f"{stored_value} (⚠️ option supprimée)"
                
        except Exception:
            return f"{stored_value} (❌ erreur)"
    
    @staticmethod
    def bulk_import_from_labels(category: str, labels: List[str]) -> Tuple[int, List[str]]:
        """
        Import en masse depuis la page admin
        Utile pour migrer des données existantes
        """
        created_count = 0
        errors = []
        
        for i, label in enumerate(labels, 1):
            success, message = DropdownCentralManager.create_option_from_admin(
                category, label.strip(), i
            )
            
            if success:
                created_count += 1
            else:
                errors.append(f"'{label}': {message}")
        
        return created_count, errors
    
    @staticmethod
    def migrate_existing_demandes():
        """
        Migre les demandes existantes en créant les options manquantes
        À utiliser UNE SEULE FOIS lors de la migration
        """
        print("🔄 Migration des demandes existantes...")
        
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        total_created = 0
        
        for category in categories:
            print(f"\n📂 Migration {category}...")
            
            # Récupérer toutes les valeurs uniques utilisées
            used_values = db.execute_query(f'''
                SELECT DISTINCT {category}
                FROM demandes 
                WHERE {category} IS NOT NULL AND {category} != ''
                ORDER BY {category}
            ''', fetch='all')
            
            if not used_values:
                print(f"   ℹ️ Aucune valeur à migrer")
                continue
            
            values_list = [row[0] for row in used_values]
            
            # Créer les options en utilisant les valeurs comme labels
            # (On assume que les valeurs actuelles sont les bons labels)
            created, errors = DropdownCentralManager.bulk_import_from_labels(
                category, values_list
            )
            
            print(f"   ✅ {created} options créées")
            if errors:
                print(f"   ⚠️ {len(errors)} erreurs:")
                for error in errors[:3]:  # Limiter l'affichage
                    print(f"      {error}")
            
            total_created += created
        
        print(f"\n🎉 Migration terminée: {total_created} options créées au total")
        return total_created

class DropdownSecurityLayer:
    """Couche de sécurité pour empêcher les insertions non autorisées"""
    
    @staticmethod
    def secure_demande_creation(demande_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        Sécurise la création d'une demande
        Filtre les valeurs non autorisées
        """
        # Valider les données
        is_valid, errors = DropdownCentralManager.validate_demande_data(demande_data)
        
        if not is_valid:
            return False, demande_data, errors
        
        # Si tout est valide, retourner les données telles quelles
        return True, demande_data, []
    
    @staticmethod
    def secure_demande_update(demande_id: int, update_data: Dict) -> Tuple[bool, Dict, List[str]]:
        """
        Sécurise la mise à jour d'une demande
        """
        # Ne valider que les champs dropdown qui sont mis à jour
        dropdown_fields = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        
        dropdown_data = {
            key: value for key, value in update_data.items() 
            if key in dropdown_fields and value is not None
        }
        
        if not dropdown_data:
            # Pas de champs dropdown à valider
            return True, update_data, []
        
        # Valider uniquement les champs dropdown
        is_valid, errors = DropdownCentralManager.validate_demande_data(dropdown_data)
        
        if not is_valid:
            return False, update_data, errors
        
        return True, update_data, []

# Fonctions utilitaires pour les vues
def get_secure_selectbox_options(category: str) -> Tuple[List[str], Dict[str, str]]:
    """
    Récupère les options sécurisées pour un selectbox Streamlit
    
    Returns:
        (values_list, value_to_label_mapping)
    """
    options = DropdownCentralManager.get_valid_options_for_form(category)
    
    values = [opt['value'] for opt in options]
    mapping = {opt['value']: opt['label'] for opt in options}
    
    return values, mapping

def display_secure_dropdown_field(category: str, label: str, key: str = None, default_value: str = None):
    """
    Affiche un champ dropdown sécurisé dans Streamlit
    """
    import streamlit as st
    
    values, mapping = get_secure_selectbox_options(category)
    
    if not values:
        return st.selectbox(label, ["Aucune option disponible"], key=key, disabled=True)
    
    # Gérer la valeur par défaut
    index = 0
    if default_value and default_value in values:
        index = values.index(default_value)
    
    return st.selectbox(
        label,
        options=values,
        index=index,
        format_func=lambda x: mapping.get(x, x),
        key=key,
        help=f"Options gérées par la page admin - {len(values)} choix disponibles"
    )

# Tests et validation
def test_normalization():
    """Test de la normalisation"""
    test_cases = [
        "NORD EST",
        "Animation Client",
        "île-de-France", 
        "Grande Distribution",
        "Client VIP",
        "Salon / Foire",
        "Commerce Indépendant"
    ]
    
    print("🧪 Test de normalisation:")
    for test_case in test_cases:
        normalized = DropdownCentralManager.normalize_label_to_value(test_case)
        print(f"  '{test_case}' → '{normalized}'")

if __name__ == "__main__":
    test_normalization()
