"""
Utilitaires pour l'affichage des options des listes déroulantes
"""
from models.dropdown_options import DropdownOptionsModel
from typing import Dict, Optional

class DropdownDisplayUtils:
    """Utilitaires pour l'affichage des options"""
    
    # Cache pour éviter de répéter les requêtes
    _options_cache = {}
    _cache_timestamp = None
    
    @staticmethod
    def is_cache_valid():
        """Vérifie si le cache est encore valide (5 minutes)"""
        from datetime import datetime, timedelta
        
        if DropdownDisplayUtils._cache_timestamp is None:
            return False
        
        return datetime.now() - DropdownDisplayUtils._cache_timestamp < timedelta(minutes=5)
    
    @staticmethod
    def get_label_for_value(category: str, value: str) -> str:
        """Récupère le label pour une valeur donnée"""
        try:
            # Traitement spécial pour les régions
            if category == 'region':
                from models.dropdown_options import DropdownOptionsModel
                return DropdownOptionsModel.get_region_display_value(value)
            
            # Utiliser le cache si disponible et valide
            cache_key = f"{category}_{value}"
            if DropdownDisplayUtils.is_cache_valid() and cache_key in DropdownDisplayUtils._options_cache:
                return DropdownDisplayUtils._options_cache[cache_key]
            
            # Récupérer toutes les options de la catégorie (y compris inactives)
            from models.database import db
            
            # Chercher d'abord dans les options actives
            result = db.execute_query("""
                SELECT label FROM dropdown_options 
                WHERE category = ? AND value = ? AND is_active = TRUE
            """, (category, value), fetch='one')
            
            if result:
                label = result['label']
                DropdownDisplayUtils._options_cache[cache_key] = label
                return label
            
            # Si pas trouvé dans les actives, chercher dans les inactives
            result = db.execute_query("""
                SELECT label FROM dropdown_options 
                WHERE category = ? AND value = ?
            """, (category, value), fetch='one')
            
            if result:
                label = f"{result['label']} (supprimée)"
                DropdownDisplayUtils._options_cache[cache_key] = label
                return label
            
            # Si vraiment pas trouvé, retourner la valeur avec indication
            fallback = f"{value} (option non trouvée)"
            DropdownDisplayUtils._options_cache[cache_key] = fallback
            
            # Mettre à jour le timestamp du cache
            if DropdownDisplayUtils._cache_timestamp is None:
                from datetime import datetime
                DropdownDisplayUtils._cache_timestamp = datetime.now()
                
            return fallback
            
        except Exception as e:
            print(f"Erreur récupération label pour {category}.{value}: {e}")
            return f"{value} (erreur)"
    
    @staticmethod
    def get_display_labels_for_demande(demande_data: Dict) -> Dict[str, str]:
        """Récupère tous les labels d'affichage pour une demande"""
        try:
            display_labels = {}
            
            # Mapping des champs vers leurs catégories
            field_mappings = {
                'budget': 'budget',
                'categorie': 'categorie', 
                'typologie_client': 'typologie_client',
                'groupe_groupement': 'groupe_groupement',
                'region': 'region'
            }
            
            for field, category in field_mappings.items():
                value = demande_data.get(field, '')
                if value:
                    display_labels[field] = DropdownDisplayUtils.get_label_for_value(category, value)
                else:
                    display_labels[field] = 'Non spécifié'
            
            return display_labels
            
        except Exception as e:
            print(f"Erreur récupération labels demande: {e}")
            return {}
    
    @staticmethod
    def clear_cache():
        """Vider le cache (utile après modification des options)"""
        DropdownDisplayUtils._options_cache.clear()
        DropdownDisplayUtils._cache_timestamp = None
        print("🧹 Cache des options vidé")
    
    @staticmethod
    def format_demande_display_text(demande_data: Dict) -> str:
        """Formate le texte d'affichage complet pour une demande"""
        try:
            labels = DropdownDisplayUtils.get_display_labels_for_demande(demande_data)
            
            # Construire le texte formaté
            display_parts = []
            
            if labels.get('budget'):
                display_parts.append(f"Budget: {labels['budget']}")
            if labels.get('categorie'):
                display_parts.append(f"Catégorie: {labels['categorie']}")
            if labels.get('typologie_client'):
                display_parts.append(f"Typologie: {labels['typologie_client']}")
            if labels.get('groupe_groupement'):
                display_parts.append(f"Groupe: {labels['groupe_groupement']}")
            if labels.get('region'):
                display_parts.append(f"Région: {labels['region']}")
            
            return " | ".join(display_parts) if display_parts else "Informations non disponibles"
            
        except Exception as e:
            print(f"Erreur formatage demande: {e}")
            return "Erreur d'affichage"

def get_dropdown_display_value(category: str, value: str, show_deleted: bool = True) -> str:
    """
    Fonction helper pour récupérer facilement un label d'affichage
    
    Args:
        category: Catégorie de l'option (budget, categorie, etc.)
        value: Valeur stockée en base de données
        show_deleted: Si True, affiche "(supprimée)" pour les options désactivées
    
    Returns:
        Label à afficher à l'utilisateur
    """
    return DropdownDisplayUtils.get_label_for_value(category, value)
