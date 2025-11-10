"""
Dropdown Options model and related operations - Version avec auto-normalisation
"""
from typing import Optional, List, Dict, Any
import pandas as pd
from models.database import db
from utils.dropdown_value_normalizer import normalize_dropdown_value, validate_normalized_value

class DropdownOptionsModel:
    """Model for managing dropdown options with automatic value normalization"""
    
    @staticmethod
    def get_options_by_category(category: str) -> List[Dict[str, Any]]:
        """Get all active options for a specific category (alias for compatibility)"""
        return DropdownOptionsModel.get_options_for_category(category)
    
    @staticmethod
    def get_options_for_category(category: str) -> List[Dict[str, Any]]:
        """Get all active options for a specific category"""
        try:
            options = db.execute_query('''
                SELECT id, value, label, order_index
                FROM dropdown_options 
                WHERE category = ? AND is_active = TRUE
                ORDER BY order_index ASC, label ASC
            ''', (category,), fetch='all')
            
            return [dict(option) for option in options] if options else []
        except Exception as e:
            print(f"Erreur récupération options {category}: {e}")
            return []
    
    @staticmethod
    def get_all_categories() -> List[str]:
        """Get all available categories"""
        try:
            categories = db.execute_query('''
                SELECT DISTINCT category
                FROM dropdown_options
                ORDER BY category
            ''', fetch='all')
            
            return [cat[0] for cat in categories] if categories else []
        except Exception as e:
            print(f"Erreur récupération catégories: {e}")
            return []
    
    @staticmethod
    def get_all_options() -> pd.DataFrame:
        """Get all options for admin management"""
        try:
            with db.get_connection() as conn:
                df = pd.read_sql_query('''
                    SELECT id, category, value, label, order_index, is_active, created_at, updated_at
                    FROM dropdown_options
                    ORDER BY category, order_index ASC, label ASC
                ''', conn)
                return df
        except Exception as e:
            print(f"Erreur récupération toutes options: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def add_option(category: str, label: str, order_index: int = 0, value: str = None, auto_normalize: bool = True) -> tuple[bool, str]:
        """Add a new option with automatic value normalization"""
        try:
            # Validation du label
            if not label or not label.strip():
                return False, "Le label est obligatoire"
            
            label = label.strip()
            
            # Auto-normalisation de la valeur si demandé (par défaut)
            if auto_normalize or not value:
                value = normalize_dropdown_value(label)
                if not validate_normalized_value(value):
                    return False, f"Impossible de générer une valeur valide à partir du label '{label}'"
            else:
                # Validation manuelle de la valeur
                if not value or not validate_normalized_value(value):
                    return False, "La valeur fournie n'est pas valide"
            
            # Vérifier que la valeur n'existe pas déjà dans cette catégorie
            existing = db.execute_query('''
                SELECT id, label FROM dropdown_options 
                WHERE category = ? AND value = ?
            ''', (category, value), fetch='one')
            
            if existing:
                return False, f"Cette valeur '{value}' existe déjà dans cette catégorie (label: '{existing['label']}')"
            
            # Si pas d'ordre spécifié, prendre le prochain numéro
            if order_index == 0:
                max_order = db.execute_query('''
                    SELECT COALESCE(MAX(order_index), 0) + 1
                    FROM dropdown_options 
                    WHERE category = ?
                ''', (category,), fetch='one')[0]
                order_index = max_order
            
            db.execute_query('''
                INSERT INTO dropdown_options (category, value, label, order_index)
                VALUES (?, ?, ?, ?)
            ''', (category, value, label, order_index))
            
            return True, f"Option ajoutée avec succès (valeur: '{value}')"
            
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def add_option_with_manual_value(category: str, value: str, label: str, order_index: int = 0) -> tuple[bool, str]:
        """Add option with manually specified value (legacy method)"""
        return DropdownOptionsModel.add_option(category, label, order_index, value, auto_normalize=False)
    
    @staticmethod
    def update_option(option_id: int, label: str = None, order_index: int = None, 
                     is_active: bool = None, auto_normalize_value: bool = True) -> tuple[bool, str]:
        """Update an existing option with automatic value normalization"""
        try:
            # Récupérer l'option actuelle
            current_option = db.execute_query('''
                SELECT category, value, label FROM dropdown_options WHERE id = ?
            ''', (option_id,), fetch='one')
            
            if not current_option:
                return False, "Option non trouvée"
            
            # Construire la requête de mise à jour dynamiquement
            set_clauses = []
            values = []
            new_value = current_option['value']  # Par défaut, garder la valeur actuelle
            
            # Si le label change, recalculer automatiquement la valeur
            if label is not None:
                label = label.strip()
                if not label:
                    return False, "Le label ne peut pas être vide"
                
                set_clauses.append("label = ?")
                values.append(label)
                
                # Auto-normalisation de la nouvelle valeur
                if auto_normalize_value:
                    new_value = normalize_dropdown_value(label)
                    if not validate_normalized_value(new_value):
                        return False, f"Impossible de générer une valeur valide à partir du label '{label}'"
                    
                    # Vérifier que la nouvelle valeur n'existe pas déjà (sauf pour cette option)
                    existing = db.execute_query('''
                        SELECT id, label FROM dropdown_options 
                        WHERE category = ? AND value = ? AND id != ?
                    ''', (current_option['category'], new_value, option_id), fetch='one')
                    
                    if existing:
                        return False, f"La valeur '{new_value}' existe déjà pour '{existing['label']}' (ID #{existing['id']})"
                    
                    # Mettre à jour aussi la valeur si elle a changé
                    if new_value != current_option['value']:
                        set_clauses.append("value = ?")
                        values.append(new_value)
            
            if order_index is not None:
                set_clauses.append("order_index = ?")
                values.append(order_index)
            
            if is_active is not None:
                set_clauses.append("is_active = ?")
                values.append(is_active)
            
            if not set_clauses:
                return False, "Aucune modification spécifiée"
            
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(option_id)
            
            query = f"UPDATE dropdown_options SET {', '.join(set_clauses)} WHERE id = ?"
            
            rows_affected = db.execute_query(query, tuple(values))
            
            if rows_affected > 0:
                # Si la valeur a changé, mettre à jour les demandes existantes
                if auto_normalize_value and label is not None and new_value != current_option['value']:
                    try:
                        category = current_option['category']
                        old_value = current_option['value']
                        
                        # Mettre à jour les demandes qui utilisent l'ancienne valeur
                        update_count = db.execute_query(f'''
                            UPDATE demandes 
                            SET {category} = ?
                            WHERE {category} = ?
                        ''', (new_value, old_value))
                        
                        if update_count > 0:
                            return True, f"Option et {update_count} demande(s) mises à jour avec succès (valeur: '{new_value}')"
                    except Exception as e:
                        # Continuer même si la mise à jour des demandes échoue
                        pass
                
                return True, f"Option mise à jour avec succès (valeur: '{new_value}')"
            else:
                return False, "Option non trouvée"
                
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def delete_option(option_id: int, force_delete: bool = False) -> tuple[bool, str]:
        """Delete an option - with choice between soft delete and hard delete"""
        try:
            # Vérifier si l'option existe
            option = db.execute_query('''
                SELECT category, value, label FROM dropdown_options WHERE id = ?
            ''', (option_id,), fetch='one')
            
            if not option:
                return False, "Option non trouvée"
            
            category, value, label = option['category'], option['value'], option['label']
            
            # Vérifier l'utilisation dans les demandes
            usage_count = db.execute_query(f'''
                SELECT COUNT(*) FROM demandes WHERE {category} = ?
            ''', (value,), fetch='one')[0]
            
            if usage_count > 0 and not force_delete:
                # Soft delete si l'option est utilisée
                db.execute_query('''
                    UPDATE dropdown_options 
                    SET is_active = FALSE, updated_at = CURRENT_TIMESTAMP 
                    WHERE id = ?
                ''', (option_id,))
                
                return True, f"Option '{label}' désactivée (utilisée dans {usage_count} demande(s))"
            
            else:
                # Hard delete si pas utilisée ou force_delete = True
                db.execute_query('''
                    DELETE FROM dropdown_options WHERE id = ?
                ''', (option_id,))
                
                action = "supprimée définitivement" if usage_count == 0 else "supprimée de force"
                return True, f"Option '{label}' {action}"
                
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def reorder_options(category: str, option_orders: List[Dict[str, int]]) -> tuple[bool, str]:
        """Reorder options in a category"""
        try:
            for item in option_orders:
                option_id = item['id']
                new_order = item['order']
                
                db.execute_query('''
                    UPDATE dropdown_options 
                    SET order_index = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ? AND category = ?
                ''', (new_order, option_id, category))
            
            return True, "Ordre mis à jour avec succès"
            
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def get_options_dict() -> Dict[str, List[Dict[str, str]]]:
        """Get all options formatted for selectboxes"""
        try:
            categories = ['budget', 'categorie', 'typologie_client', 
                         'groupe_groupement', 'region', 'agence']
            
            options_dict = {}
            for category in categories:
                options = DropdownOptionsModel.get_options_for_category(category)
                options_dict[category] = [
                    {'value': opt['value'], 'label': opt['label']} 
                    for opt in options
                ]
            
            return options_dict
            
        except Exception as e:
            print(f"Erreur formatage options: {e}")
            return {}
    
    @staticmethod
    def get_category_stats() -> Dict[str, Any]:
        """Get statistics by category"""
        try:
            with db.get_connection() as conn:
                stats = pd.read_sql_query('''
                    SELECT category, 
                           COUNT(*) as total,
                           SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as active,
                           SUM(CASE WHEN is_active THEN 0 ELSE 1 END) as inactive
                    FROM dropdown_options 
                    GROUP BY category
                    ORDER BY category
                ''', conn)
                
                return stats.to_dict('records') if not stats.empty else []
        except Exception as e:
            print(f"Erreur stats catégories: {e}")
            return []
    
    @staticmethod
    def search_options(search_term: str, category: str = None) -> pd.DataFrame:
        """Search options by term"""
        try:
            search_term = f"%{search_term}%"
            
            if category:
                query = '''
                    SELECT id, category, value, label, order_index, is_active
                    FROM dropdown_options
                    WHERE category = ? AND (value LIKE ? OR label LIKE ?)
                    ORDER BY category, order_index ASC, label ASC
                '''
                params = (category, search_term, search_term)
            else:
                query = '''
                    SELECT id, category, value, label, order_index, is_active
                    FROM dropdown_options
                    WHERE value LIKE ? OR label LIKE ?
                    ORDER BY category, order_index ASC, label ASC
                '''
                params = (search_term, search_term)
            
            with db.get_connection() as conn:
                df = pd.read_sql_query(query, conn, params=params)
                return df
                
        except Exception as e:
            print(f"Erreur recherche options: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def import_options_from_dict(options_dict: Dict[str, List[str]]) -> tuple[bool, str]:
        """Import options from dictionary (for migration) with auto-normalization"""
        try:
            imported_count = 0
            
            for category, options_list in options_dict.items():
                for idx, option_label in enumerate(options_list, 1):
                    # Utiliser la fonction d'ajout avec auto-normalisation
                    success, message = DropdownOptionsModel.add_option(
                        category, option_label, idx
                    )
                    
                    if success:
                        imported_count += 1
            
            return True, f"{imported_count} options importées avec succès"
            
        except Exception as e:
            return False, f"Erreur import: {e}"
    
    @staticmethod
    def batch_normalize_existing_values() -> tuple[bool, str]:
        """Normalise toutes les valeurs existantes selon la nouvelle logique"""
        try:
            options = db.execute_query('''
                SELECT id, category, value, label
                FROM dropdown_options
                ORDER BY category, id
            ''', fetch='all')
            
            if not options:
                return True, "Aucune option à traiter"
            
            updated_count = 0
            conflicts = []
            
            for option in options:
                option_id = option['id']
                category = option['category']
                old_value = option['value']
                label = option['label']
                
                # Calculer la nouvelle valeur
                new_value = normalize_dropdown_value(label)
                
                # Si la valeur ne change pas, passer au suivant
                if old_value == new_value:
                    continue
                
                # Vérifier s'il y a conflit
                existing = db.execute_query('''
                    SELECT id, label FROM dropdown_options
                    WHERE category = ? AND value = ? AND id != ?
                ''', (category, new_value, option_id), fetch='one')
                
                if existing:
                    conflicts.append({
                        'option_id': option_id,
                        'label': label,
                        'old_value': old_value,
                        'new_value': new_value,
                        'conflict_label': existing['label']
                    })
                    continue
                
                # Mettre à jour la valeur
                db.execute_query('''
                    UPDATE dropdown_options 
                    SET value = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (new_value, option_id))
                
                # Mettre à jour les demandes qui utilisent cette valeur
                try:
                    db.execute_query(f'''
                        UPDATE demandes 
                        SET {category} = ?
                        WHERE {category} = ?
                    ''', (new_value, old_value))
                except:
                    pass  # Ignorer si la colonne n'existe pas
                
                updated_count += 1
            
            message = f"{updated_count} options normalisées"
            if conflicts:
                message += f", {len(conflicts)} conflits détectés"
            
            return True, message
            
        except Exception as e:
            return False, f"Erreur normalisation: {e}"
    
    @staticmethod
    def preview_normalization(label: str) -> Dict[str, Any]:
        """Aperçu de la normalisation d'un label"""
        from utils.dropdown_value_normalizer import preview_normalization
        return preview_normalization(label)
    
    @staticmethod
    def format_region_display(stored_value: str) -> str:
        """Transforme une valeur stockée en région vers son affichage final
        Ex: "nord_est" -> "NORD EST"
        """
        if not stored_value:
            return "Non spécifié"
        
        # Remplacer les underscores par des espaces et mettre en majuscules
        return stored_value.replace('_', ' ').upper()
    
    @staticmethod
    def get_region_display_value(stored_value: str) -> str:
        """Récupère la valeur d'affichage d'une région depuis sa valeur stockée
        Utilise d'abord la table dropdown_options, sinon applique la transformation
        """
        if not stored_value:
            return "Non spécifié"
        
        try:
            # D'abord chercher dans la table dropdown_options
            option = db.execute_query('''
                SELECT label FROM dropdown_options 
                WHERE category = 'region' AND value = ? AND is_active = TRUE
            ''', (stored_value,), fetch='one')
            
            if option:
                return option['label']
            else:
                # Si pas trouvé, appliquer la transformation automatique
                return DropdownOptionsModel.format_region_display(stored_value)
                
        except Exception as e:
            print(f"Erreur récupération région: {e}")
            return DropdownOptionsModel.format_region_display(stored_value)
