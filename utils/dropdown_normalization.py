"""
Système de normalisation pour les valeurs des listes déroulantes
"""
import re
from typing import Dict, Optional
from models.dropdown_options import DropdownOptionsModel

class DropdownNormalizer:
    """Classe pour normaliser les valeurs des dropdown"""
    
    @staticmethod
    def normalize_label_to_value(label: str) -> str:
        """
        Convertit un label d'affichage en valeur technique pour stockage
        Ex: "NORD EST" -> "nord_est"
        """
        if not label:
            return ""
        
        # Convertir en minuscules
        normalized = label.lower()
        
        # Remplacer les espaces et caractères spéciaux par des underscores
        normalized = re.sub(r'[^a-z0-9]+', '_', normalized)
        
        # Supprimer les underscores en début et fin
        normalized = normalized.strip('_')
        
        # Supprimer les underscores multiples
        normalized = re.sub(r'_+', '_', normalized)
        
        return normalized
    
    @staticmethod
    def find_or_create_option(category: str, display_label: str) -> tuple[bool, str]:
        """
        Trouve une option existante ou en crée une nouvelle
        
        Args:
            category: Catégorie (budget, categorie, etc.)
            display_label: Label affiché à l'utilisateur
            
        Returns:
            (success, value_to_store)
        """
        try:
            # D'abord chercher si une option avec ce label existe déjà
            from models.database import db
            
            existing_option = db.execute_query('''
                SELECT value FROM dropdown_options
                WHERE category = ? AND label = ? AND is_active = TRUE
            ''', (category, display_label), fetch='one')
            
            if existing_option:
                return True, existing_option['value']
            
            # Sinon, générer une valeur normalisée
            normalized_value = DropdownNormalizer.normalize_label_to_value(display_label)
            
            # Vérifier si cette valeur existe déjà
            existing_value = db.execute_query('''
                SELECT id FROM dropdown_options
                WHERE category = ? AND value = ?
            ''', (category, normalized_value), fetch='one')
            
            if existing_value:
                # La valeur existe, mettre à jour le label si nécessaire
                success, message = DropdownOptionsModel.update_option(
                    existing_value['id'], 
                    label=display_label,
                    is_active=True
                )
                return success, normalized_value
            else:
                # Créer une nouvelle option
                success, message = DropdownOptionsModel.add_option(
                    category, normalized_value, display_label
                )
                return success, normalized_value
                
        except Exception as e:
            print(f"Erreur find_or_create_option: {e}")
            # En cas d'erreur, retourner la valeur normalisée
            return True, DropdownNormalizer.normalize_label_to_value(display_label)
    
    @staticmethod
    def repair_existing_data():
        """
        Répare les données existantes en créant les options manquantes
        """
        from models.database import db
        
        print("🔧 Réparation des données existantes...")
        
        # Récupérer toutes les demandes avec leurs valeurs
        demandes = db.execute_query('''
            SELECT id, budget, categorie, typologie_client, groupe_groupement, region
            FROM demandes
        ''', fetch='all')
        
        if not demandes:
            print("✅ Aucune demande à réparer")
            return
        
        categories = ['budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region']
        repairs_made = 0
        
        for demande in demandes:
            demande_id = demande['id']
            
            for category in categories:
                stored_value = demande[category]
                
                if stored_value:
                    # Vérifier si l'option existe
                    option = db.execute_query('''
                        SELECT label FROM dropdown_options
                        WHERE category = ? AND value = ? AND is_active = TRUE
                    ''', (category, stored_value), fetch='one')
                    
                    if not option:
                        # Créer l'option manquante
                        # Générer un label à partir de la valeur
                        generated_label = stored_value.replace('_', ' ').title()
                        
                        success, message = DropdownOptionsModel.add_option(
                            category, stored_value, generated_label
                        )
                        
                        if success:
                            print(f"  ✅ Option créée: {category}.{stored_value} = '{generated_label}'")
                            repairs_made += 1
                        else:
                            print(f"  ❌ Erreur création {category}.{stored_value}: {message}")
        
        print(f"🎉 Réparation terminée: {repairs_made} options créées")
    
    @staticmethod
    def create_mapping_for_inconsistent_data():
        """
        Crée un mapping pour les données incohérentes détectées
        """
        print("🗺️ Création du mapping pour données incohérentes...")
        
        # Mapping manuel pour les cas détectés
        mappings = {
            'budget': {
                'SALES': 'sales',  # Normaliser SALES
                'Budget Marketing': 'budget_marketing',
                'Budget Commercial': 'budget_commercial',
            },
            'categorie': {
                'ANIMATION CLIENT': 'animation_client',  # Normaliser
                'SALON FOIRE': 'salon_foire',
                'Salon / Foire': 'salon_foire',
            },
            'typologie_client': {
                'INDEPENDANT': 'independant',  # Normaliser
                'CLIENT VIP': 'client_vip',
                'Prospect': 'prospect',
            },
            'groupe_groupement': {
                'REXEL': 'rexel',  # Normaliser le nom de l'entreprise
                'Grande Distribution': 'grande_distribution',
                'Commerce Indépendant': 'commerce_independant',
            },
            'region': {
                'NORD EST': 'nord_est',  # Normaliser automatiquement
                'Île-de-France': 'ile_de_france',
                'Nord': 'nord',
                'Sud': 'sud',
                'Est': 'est',
                'Ouest': 'ouest',
            }
        }
        
        created_count = 0
        
        for category, category_mappings in mappings.items():
            for display_label, correct_value in category_mappings.items():
                # Créer ou mettre à jour l'option
                try:
                    success, message = DropdownOptionsModel.add_option(
                        category, correct_value, display_label
                    )
                    
                    if success:
                        print(f"  ✅ Mapping créé: {category}.{correct_value} = '{display_label}'")
                        created_count += 1
                    else:
                        # L'option existe déjà, mettre à jour le label
                        from models.database import db
                        option = db.execute_query('''
                            SELECT id FROM dropdown_options
                            WHERE category = ? AND value = ?
                        ''', (category, correct_value), fetch='one')
                        
                        if option:
                            DropdownOptionsModel.update_option(
                                option['id'], 
                                label=display_label,
                                is_active=True
                            )
                            print(f"  🔄 Mapping mis à jour: {category}.{correct_value} = '{display_label}'")
                        
                except Exception as e:
                    print(f"  ❌ Erreur mapping {category}.{correct_value}: {e}")
        
        print(f"📊 {created_count} nouveaux mappings créés")
        
        return mappings

class DropdownValueManager:
    """Gestionnaire pour les valeurs des dropdown dans les formulaires"""
    
    @staticmethod
    def prepare_selectbox_options(category: str) -> tuple[list, dict]:
        """
        Prépare les options pour un selectbox Streamlit
        
        Returns:
            (liste_des_valeurs, mapping_value_to_label)
        """
        try:
            options = DropdownOptionsModel.get_options_for_category(category)
            
            if not options:
                return [], {}
            
            values = [opt['value'] for opt in options]
            value_to_label = {opt['value']: opt['label'] for opt in options}
            
            return values, value_to_label
            
        except Exception as e:
            print(f"Erreur préparation options {category}: {e}")
            return [], {}
    
    @staticmethod
    def get_display_value(category: str, stored_value: str) -> str:
        """
        Récupère la valeur d'affichage pour une valeur stockée
        """
        if not stored_value:
            return "Non spécifié"
        
        try:
            from models.database import db
            
            option = db.execute_query('''
                SELECT label FROM dropdown_options
                WHERE category = ? AND value = ? AND is_active = TRUE
            ''', (category, stored_value), fetch='one')
            
            if option:
                return option['label']
            else:
                # Option manquante, retourner la valeur formatée
                return stored_value.replace('_', ' ').title() + " (option manquante)"
                
        except Exception as e:
            print(f"Erreur récupération display_value {category}.{stored_value}: {e}")
            return f"{stored_value} (erreur)"

# Script de test et réparation
def test_normalization():
    """Test de la normalisation"""
    test_cases = [
        "NORD EST",
        "ANIMATION CLIENT", 
        "Budget Marketing",
        "île-de-France",
        "Grand Distribution",
        "Client VIP"
    ]
    
    print("🧪 Test de normalisation:")
    for test_case in test_cases:
        normalized = DropdownNormalizer.normalize_label_to_value(test_case)
        print(f"  '{test_case}' -> '{normalized}'")

def repair_all_data():
    """Répare toutes les données du système"""
    print("🔧 === RÉPARATION COMPLÈTE DES DONNÉES ===\n")
    
    # 1. Créer les mappings pour les données incohérentes
    DropdownNormalizer.create_mapping_for_inconsistent_data()
    
    print()
    
    # 2. Réparer les données existantes
    DropdownNormalizer.repair_existing_data()
    
    print()
    
    # 3. Vider le cache
    from utils.dropdown_display import DropdownDisplayUtils
    DropdownDisplayUtils.clear_cache()
    
    print("✅ Réparation complète terminée !")

if __name__ == "__main__":
    test_normalization()
    print()
    repair_all_data()
