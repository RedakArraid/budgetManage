"""
Modèle pour la gestion des budgets utilisateurs
"""
from models.database import db
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserBudgetModel:
    """Modèle pour gérer les budgets alloués aux utilisateurs"""
    
    @staticmethod
    def create_budget(user_id: int, fiscal_year: int, allocated_budget: float) -> bool:
        """
        Créer ou mettre à jour un budget utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            fiscal_year: Année fiscale
            allocated_budget: Budget alloué
            
        Returns:
            bool: True si succès
        """
        try:
            db.execute_query("""
                INSERT OR REPLACE INTO user_budgets 
                (user_id, fiscal_year, allocated_budget, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, fiscal_year, allocated_budget))
            
            logger.info(f"Budget créé/mis à jour pour utilisateur {user_id} année {fiscal_year}: {allocated_budget}€")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création budget: {e}")
            return False
    
    @staticmethod
    def get_user_budget(user_id: int, fiscal_year: int) -> Optional[Dict[str, Any]]:
        """
        Obtenir le budget d'un utilisateur pour une année
        
        Args:
            user_id: ID de l'utilisateur
            fiscal_year: Année fiscale
            
        Returns:
            Dict contenant les informations du budget ou None
        """
        try:
            result = db.execute_query("""
                SELECT ub.*, u.nom, u.prenom, u.email, u.role
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.user_id = ? AND ub.fiscal_year = ?
            """, (user_id, fiscal_year), fetch='one')
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Erreur récupération budget: {e}")
            return None
    
    @staticmethod
    def get_all_budgets_for_year(fiscal_year: int) -> List[Dict[str, Any]]:
        """
        Obtenir tous les budgets pour une année
        
        Args:
            fiscal_year: Année fiscale
            
        Returns:
            Liste des budgets
        """
        try:
            results = db.execute_query("""
                SELECT ub.*, u.nom, u.prenom, u.email, u.role, u.region
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.fiscal_year = ?
                ORDER BY u.nom, u.prenom
            """, (fiscal_year,), fetch='all')
            
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Erreur récupération budgets année: {e}")
            return []
    
    @staticmethod
    def get_budgets_by_user(user_id: int) -> List[Dict[str, Any]]:
        """
        Obtenir tous les budgets d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            
        Returns:
            Liste des budgets de l'utilisateur
        """
        try:
            results = db.execute_query("""
                SELECT ub.*, u.nom, u.prenom, u.email, u.role
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.user_id = ?
                ORDER BY ub.fiscal_year DESC
            """, (user_id,), fetch='all')
            
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Erreur récupération budgets utilisateur: {e}")
            return []
    
    @staticmethod
    def delete_budget(user_id: int, fiscal_year: int) -> bool:
        """
        Supprimer un budget utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            fiscal_year: Année fiscale
            
        Returns:
            bool: True si succès
        """
        try:
            rows_affected = db.execute_query("""
                DELETE FROM user_budgets 
                WHERE user_id = ? AND fiscal_year = ?
            """, (user_id, fiscal_year))
            
            if rows_affected > 0:
                logger.info(f"Budget supprimé pour utilisateur {user_id} année {fiscal_year}")
                return True
            else:
                logger.warning(f"Aucun budget trouvé pour suppression: utilisateur {user_id} année {fiscal_year}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur suppression budget: {e}")
            return False
    
    @staticmethod
    def get_budget_summary_by_year(fiscal_year: int) -> Dict[str, Any]:
        """
        Obtenir un résumé des budgets par année
        
        Args:
            fiscal_year: Année fiscale
            
        Returns:
            Dict contenant les statistiques
        """
        try:
            # Budget total alloué
            total_result = db.execute_query("""
                SELECT SUM(allocated_budget) as total_allocated
                FROM user_budgets 
                WHERE fiscal_year = ?
            """, (fiscal_year,), fetch='one')
            
            total_allocated = total_result['total_allocated'] if total_result else 0
            
            # Budget par rôle
            by_role_results = db.execute_query("""
                SELECT u.role, SUM(ub.allocated_budget) as total_budget, COUNT(*) as user_count
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.fiscal_year = ?
                GROUP BY u.role
                ORDER BY total_budget DESC
            """, (fiscal_year,), fetch='all')
            
            by_role = [dict(row) for row in by_role_results] if by_role_results else []
            
            # Budget par région
            by_region_results = db.execute_query("""
                SELECT u.region, SUM(ub.allocated_budget) as total_budget, COUNT(*) as user_count
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.fiscal_year = ? AND u.region IS NOT NULL
                GROUP BY u.region
                ORDER BY total_budget DESC
            """, (fiscal_year,), fetch='all')
            
            by_region = [dict(row) for row in by_region_results] if by_region_results else []
            
            # Utilisateurs avec/sans budget
            users_with_budget = db.execute_query("""
                SELECT COUNT(DISTINCT ub.user_id) as count
                FROM user_budgets ub
                WHERE ub.fiscal_year = ?
            """, (fiscal_year,), fetch='one')
            
            total_active_users = db.execute_query("""
                SELECT COUNT(*) as count
                FROM users 
                WHERE is_active = TRUE
            """, fetch='one')
            
            with_budget_count = users_with_budget['count'] if users_with_budget else 0
            total_users_count = total_active_users['count'] if total_active_users else 0
            without_budget_count = total_users_count - with_budget_count
            
            return {
                'fiscal_year': fiscal_year,
                'total_allocated': float(total_allocated) if total_allocated else 0.0,
                'total_users': total_users_count,
                'users_with_budget': with_budget_count,
                'users_without_budget': without_budget_count,
                'by_role': by_role,
                'by_region': by_region,
                'average_budget': float(total_allocated / with_budget_count) if with_budget_count > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul résumé budgets: {e}")
            return {
                'fiscal_year': fiscal_year,
                'total_allocated': 0.0,
                'total_users': 0,
                'users_with_budget': 0,
                'users_without_budget': 0,
                'by_role': [],
                'by_region': [],
                'average_budget': 0.0
            }
    
    @staticmethod
    def get_budget_consumption(user_id: int, fiscal_year: int) -> Dict[str, Any]:
        """
        Calculer la consommation de budget d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            fiscal_year: Année fiscale
            
        Returns:
            Dict contenant les informations de consommation
        """
        try:
            # Budget alloué
            budget_info = UserBudgetModel.get_user_budget(user_id, fiscal_year)
            allocated_budget = budget_info['allocated_budget'] if budget_info else 0.0
            
            # Budget consommé (demandes validées)
            consumed_result = db.execute_query("""
                SELECT SUM(montant) as consumed
                FROM demandes 
                WHERE user_id = ? 
                AND status = 'validee'
                AND strftime('%Y', date_evenement) = ?
            """, (user_id, str(fiscal_year)), fetch='one')
            
            consumed_budget = consumed_result['consumed'] if consumed_result['consumed'] else 0.0
            
            # Budget en attente (demandes en cours de validation)
            pending_result = db.execute_query("""
                SELECT SUM(montant) as pending
                FROM demandes 
                WHERE user_id = ? 
                AND status IN ('en_attente_dr', 'en_attente_financier')
                AND strftime('%Y', date_evenement) = ?
            """, (user_id, str(fiscal_year)), fetch='one')
            
            pending_budget = pending_result['pending'] if pending_result['pending'] else 0.0
            
            # Calculs
            remaining_budget = allocated_budget - consumed_budget - pending_budget
            consumption_rate = (consumed_budget / allocated_budget * 100) if allocated_budget > 0 else 0
            
            return {
                'user_id': user_id,
                'fiscal_year': fiscal_year,
                'allocated_budget': float(allocated_budget),
                'consumed_budget': float(consumed_budget),
                'pending_budget': float(pending_budget),
                'remaining_budget': float(remaining_budget),
                'consumption_rate': round(consumption_rate, 2),
                'is_over_budget': remaining_budget < 0
            }
            
        except Exception as e:
            logger.error(f"Erreur calcul consommation budget: {e}")
            return {
                'user_id': user_id,
                'fiscal_year': fiscal_year,
                'allocated_budget': 0.0,
                'consumed_budget': 0.0,
                'pending_budget': 0.0,
                'remaining_budget': 0.0,
                'consumption_rate': 0.0,
                'is_over_budget': False
            }
    
    @staticmethod
    def bulk_create_budgets(budgets_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Créer plusieurs budgets en une seule opération
        
        Args:
            budgets_data: Liste de dictionnaires avec user_id, fiscal_year, allocated_budget
            
        Returns:
            Dict avec le nombre de succès et d'échecs
        """
        success_count = 0
        error_count = 0
        
        for budget_data in budgets_data:
            try:
                user_id = budget_data.get('user_id')
                fiscal_year = budget_data.get('fiscal_year')
                allocated_budget = budget_data.get('allocated_budget')
                
                if user_id and fiscal_year and allocated_budget is not None:
                    if UserBudgetModel.create_budget(user_id, fiscal_year, allocated_budget):
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    error_count += 1
                    logger.warning(f"Données budget invalides: {budget_data}")
                    
            except Exception as e:
                error_count += 1
                logger.error(f"Erreur création budget en lot: {e}")
        
        logger.info(f"Création budgets en lot: {success_count} succès, {error_count} erreurs")
        return {
            'success_count': success_count,
            'error_count': error_count,
            'total_processed': len(budgets_data)
        }
    
    @staticmethod
    def copy_budgets_to_next_year(source_year: int, target_year: int, 
                                 increase_percentage: float = 0.0) -> Dict[str, int]:
        """
        Copier les budgets d'une année vers l'année suivante
        
        Args:
            source_year: Année source
            target_year: Année cible
            increase_percentage: Pourcentage d'augmentation (ex: 5.0 pour +5%)
            
        Returns:
            Dict avec le nombre de succès et d'échecs
        """
        try:
            # Récupérer tous les budgets de l'année source
            source_budgets = UserBudgetModel.get_all_budgets_for_year(source_year)
            
            success_count = 0
            error_count = 0
            
            for budget in source_budgets:
                try:
                    # Calculer le nouveau montant avec augmentation
                    old_amount = budget['allocated_budget']
                    new_amount = old_amount * (1 + increase_percentage / 100)
                    
                    if UserBudgetModel.create_budget(
                        budget['user_id'], 
                        target_year, 
                        new_amount
                    ):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Erreur copie budget utilisateur {budget['user_id']}: {e}")
            
            logger.info(f"Copie budgets {source_year}→{target_year}: {success_count} succès, {error_count} erreurs")
            return {
                'success_count': success_count,
                'error_count': error_count,
                'source_year': source_year,
                'target_year': target_year,
                'increase_percentage': increase_percentage
            }
            
        except Exception as e:
            logger.error(f"Erreur copie budgets vers année suivante: {e}")
            return {
                'success_count': 0,
                'error_count': 0,
                'source_year': source_year,
                'target_year': target_year,
                'increase_percentage': increase_percentage
            }
