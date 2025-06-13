"""
Version migrée du UserBudgetModel pour utiliser by (string) au lieu de fiscal_year (int)
Remplace complètement models/user_budget.py
"""
from models.database import db
from typing import Optional, List, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class UserBudgetModel:
    """Modèle pour gérer les budgets alloués aux utilisateurs - Version BY uniquement"""
    
    @staticmethod
    def create_budget(user_id: int, by: str, allocated_budget: float) -> bool:
        """
        Créer ou mettre à jour un budget utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            allocated_budget: Budget alloué
            
        Returns:
            bool: True si succès
        """
        try:
            # Validation format BY
            from utils.fiscal_year_utils import validate_fiscal_year_format, validate_fiscal_year
            
            if not validate_fiscal_year_format(by):
                logger.error(f"Format année fiscale invalide: {by}")
                return False
            
            # Validation année autorisée (optionnelle - si pas dans dropdowns, on accepte quand même)
            if not validate_fiscal_year(by):
                logger.warning(f"Année fiscale non configurée dans dropdowns: {by}")
            
            db.execute_query("""
                INSERT OR REPLACE INTO user_budgets 
                (user_id, by, allocated_budget, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, by, allocated_budget))
            
            logger.info(f"Budget créé/mis à jour pour utilisateur {user_id} année {by}: {allocated_budget}€")
            return True
            
        except Exception as e:
            logger.error(f"Erreur création budget: {e}")
            return False
    
    @staticmethod
    def get_user_budget(user_id: int, by: str) -> Optional[Dict[str, Any]]:
        """
        Obtenir le budget d'un utilisateur pour une année
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Dict contenant les informations du budget ou None
        """
        try:
            result = db.execute_query("""
                SELECT ub.*, u.nom, u.prenom, u.email, u.role
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.user_id = ? AND ub.by = ?
            """, (user_id, by), fetch='one')
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Erreur récupération budget: {e}")
            return None
    
    @staticmethod
    def get_all_budgets_for_year(by: str) -> List[Dict[str, Any]]:
        """
        Obtenir tous les budgets pour une année
        
        Args:
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Liste des budgets
        """
        try:
            results = db.execute_query("""
                SELECT ub.*, u.nom, u.prenom, u.email, u.role, u.region
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.by = ?
                ORDER BY u.nom, u.prenom
            """, (by,), fetch='all')
            
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
                ORDER BY ub.by DESC
            """, (user_id,), fetch='all')
            
            return [dict(row) for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Erreur récupération budgets utilisateur: {e}")
            return []
    
    @staticmethod
    def delete_budget(user_id: int, by: str) -> bool:
        """
        Supprimer un budget utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            bool: True si succès
        """
        try:
            rows_affected = db.execute_query("""
                DELETE FROM user_budgets 
                WHERE user_id = ? AND by = ?
            """, (user_id, by))
            
            if rows_affected > 0:
                logger.info(f"Budget supprimé pour utilisateur {user_id} année {by}")
                return True
            else:
                logger.warning(f"Aucun budget trouvé pour suppression: utilisateur {user_id} année {by}")
                return False
                
        except Exception as e:
            logger.error(f"Erreur suppression budget: {e}")
            return False
    
    @staticmethod
    def get_budget_summary_by_year(by: str) -> Dict[str, Any]:
        """
        Obtenir un résumé des budgets par année
        
        Args:
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Dict contenant les statistiques
        """
        try:
            # Budget total alloué
            total_result = db.execute_query("""
                SELECT SUM(allocated_budget) as total_allocated
                FROM user_budgets 
                WHERE by = ?
            """, (by,), fetch='one')
            
            total_allocated = total_result['total_allocated'] if total_result else 0
            
            # Budget par rôle
            by_role_results = db.execute_query("""
                SELECT u.role, SUM(ub.allocated_budget) as total_budget, COUNT(*) as user_count
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.by = ?
                GROUP BY u.role
                ORDER BY total_budget DESC
            """, (by,), fetch='all')
            
            by_role = [dict(row) for row in by_role_results] if by_role_results else []
            
            # Budget par région
            by_region_results = db.execute_query("""
                SELECT u.region, SUM(ub.allocated_budget) as total_budget, COUNT(*) as user_count
                FROM user_budgets ub
                JOIN users u ON ub.user_id = u.id
                WHERE ub.by = ? AND u.region IS NOT NULL
                GROUP BY u.region
                ORDER BY total_budget DESC
            """, (by,), fetch='all')
            
            by_region = [dict(row) for row in by_region_results] if by_region_results else []
            
            # Utilisateurs avec/sans budget
            users_with_budget = db.execute_query("""
                SELECT COUNT(DISTINCT ub.user_id) as count
                FROM user_budgets ub
                WHERE ub.by = ?
            """, (by,), fetch='one')
            
            total_active_users = db.execute_query("""
                SELECT COUNT(*) as count
                FROM users 
                WHERE is_active = TRUE
            """, fetch='one')
            
            with_budget_count = users_with_budget['count'] if users_with_budget else 0
            total_users_count = total_active_users['count'] if total_active_users else 0
            without_budget_count = total_users_count - with_budget_count
            
            return {
                'by': by,
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
                'by': by,
                'total_allocated': 0.0,
                'total_users': 0,
                'users_with_budget': 0,
                'users_without_budget': 0,
                'by_role': [],
                'by_region': [],
                'average_budget': 0.0
            }
    
    @staticmethod
    def get_budget_consumption(user_id: int, by: str) -> Dict[str, Any]:
        """
        Calculer la consommation de budget d'un utilisateur
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Dict contenant les informations de consommation
        """
        try:
            # Budget alloué
            budget_info = UserBudgetModel.get_user_budget(user_id, by)
            allocated_budget = budget_info['allocated_budget'] if budget_info else 0.0
            
            # Budget consommé (demandes validées pour cette année fiscale BY)
            consumed_result = db.execute_query("""
                SELECT SUM(montant) as consumed
                FROM demandes 
                WHERE user_id = ? 
                AND status = 'validee'
                AND by = ?
            """, (user_id, by), fetch='one')
            
            consumed_budget = consumed_result['consumed'] if consumed_result['consumed'] else 0.0
            
            # Budget en attente (demandes en cours de validation pour cette année fiscale BY)
            pending_result = db.execute_query("""
                SELECT SUM(montant) as pending
                FROM demandes 
                WHERE user_id = ? 
                AND status IN ('en_attente_dr', 'en_attente_financier')
                AND by = ?
            """, (user_id, by), fetch='one')
            
            pending_budget = pending_result['pending'] if pending_result['pending'] else 0.0
            
            # Calculs
            remaining_budget = allocated_budget - consumed_budget - pending_budget
            consumption_rate = (consumed_budget / allocated_budget * 100) if allocated_budget > 0 else 0
            
            return {
                'user_id': user_id,
                'by': by,
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
                'by': by,
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
            budgets_data: Liste de dictionnaires avec user_id, by, allocated_budget
            
        Returns:
            Dict avec le nombre de succès et d'échecs
        """
        success_count = 0
        error_count = 0
        
        for budget_data in budgets_data:
            try:
                user_id = budget_data.get('user_id')
                by = budget_data.get('by')
                allocated_budget = budget_data.get('allocated_budget')
                
                if user_id and by and allocated_budget is not None:
                    if UserBudgetModel.create_budget(user_id, by, allocated_budget):
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
    def copy_budgets_to_next_year(source_by: str, target_by: str, 
                                 increase_percentage: float = 0.0) -> Dict[str, int]:
        """
        Copier les budgets d'une année vers l'année suivante
        
        Args:
            source_by: Année source format BYXX (ex: "BY24")
            target_by: Année cible format BYXX (ex: "BY25")
            increase_percentage: Pourcentage d'augmentation (ex: 5.0 pour +5%)
            
        Returns:
            Dict avec le nombre de succès et d'échecs
        """
        try:
            # Récupérer tous les budgets de l'année source
            source_budgets = UserBudgetModel.get_all_budgets_for_year(source_by)
            
            success_count = 0
            error_count = 0
            
            for budget in source_budgets:
                try:
                    # Calculer le nouveau montant avec augmentation
                    old_amount = budget['allocated_budget']
                    new_amount = old_amount * (1 + increase_percentage / 100)
                    
                    if UserBudgetModel.create_budget(
                        budget['user_id'], 
                        target_by, 
                        new_amount
                    ):
                        success_count += 1
                    else:
                        error_count += 1
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"Erreur copie budget utilisateur {budget['user_id']}: {e}")
            
            logger.info(f"Copie budgets {source_by}→{target_by}: {success_count} succès, {error_count} erreurs")
            return {
                'success_count': success_count,
                'error_count': error_count,
                'source_by': source_by,
                'target_by': target_by,
                'increase_percentage': increase_percentage
            }
            
        except Exception as e:
            logger.error(f"Erreur copie budgets vers année suivante: {e}")
            return {
                'success_count': 0,
                'error_count': 0,
                'source_by': source_by,
                'target_by': target_by,
                'increase_percentage': increase_percentage
            }
    
    @staticmethod
    def get_all_fiscal_years() -> List[str]:
        """
        Obtenir toutes les années fiscales ayant des budgets
        
        Returns:
            Liste des années fiscales (format BYXX) triées
        """
        try:
            results = db.execute_query("""
                SELECT DISTINCT by
                FROM user_budgets 
                WHERE by IS NOT NULL AND by != ''
                ORDER BY by
            """, fetch='all')
            
            return [row['by'] for row in results] if results else []
            
        except Exception as e:
            logger.error(f"Erreur récupération années fiscales: {e}")
            return []
    
    @staticmethod
    def get_unified_budget_dashboard(user_id: int, by: str) -> Dict[str, Any]:
        """
        Dashboard unifié budget + demandes pour une année fiscale
        NOUVELLE FONCTIONNALITÉ débloquée par la migration !
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Dict avec vue unifiée budget/consommation
        """
        try:
            # Récupérer consommation (inclut budget alloué)
            consumption = UserBudgetModel.get_budget_consumption(user_id, by)
            
            # Récupérer détails demandes pour cette année
            from models.demande import DemandeModel
            user_info = db.execute_query("SELECT role FROM users WHERE id = ?", (user_id,), fetch='one')
            role = user_info['role'] if user_info else 'tc'
            
            # Utiliser le filtre fiscal_year_filter qui maintenant fonctionne !
            import pandas as pd
            demandes_df = DemandeModel.get_demandes_for_user(user_id, role, fiscal_year_filter=by)
            
            if not demandes_df.empty:
                # Statistiques demandes
                validees = demandes_df[demandes_df['status'] == 'validee']
                en_cours = demandes_df[demandes_df['status'].isin(['en_attente_dr', 'en_attente_financier'])]
                rejetees = demandes_df[demandes_df['status'] == 'rejetee']
                
                demandes_stats = {
                    'total_demandes': len(demandes_df),
                    'validees_count': len(validees),
                    'en_cours_count': len(en_cours),
                    'rejetees_count': len(rejetees),
                    'montant_valide': float(validees['montant'].sum() if not validees.empty else 0),
                    'montant_en_cours': float(en_cours['montant'].sum() if not en_cours.empty else 0),
                }
            else:
                demandes_stats = {
                    'total_demandes': 0,
                    'validees_count': 0,
                    'en_cours_count': 0,
                    'rejetees_count': 0,
                    'montant_valide': 0.0,
                    'montant_en_cours': 0.0,
                }
            
            # Combiner données budget + demandes
            dashboard = {
                **consumption,  # Inclut allocated_budget, consumed_budget, etc.
                **demandes_stats,  # Inclut total_demandes, validees_count, etc.
                'budget_health': 'good' if consumption['remaining_budget'] > 0 else 'warning' if consumption['remaining_budget'] > -1000 else 'danger'
            }
            
            return dashboard
            
        except Exception as e:
            logger.error(f"Erreur dashboard unifié: {e}")
            return {
                'user_id': user_id,
                'by': by,
                'allocated_budget': 0.0,
                'consumed_budget': 0.0,
                'pending_budget': 0.0,
                'remaining_budget': 0.0,
                'consumption_rate': 0.0,
                'is_over_budget': False,
                'total_demandes': 0,
                'validees_count': 0,
                'en_cours_count': 0,
                'rejetees_count': 0,
                'montant_valide': 0.0,
                'montant_en_cours': 0.0,
                'budget_health': 'unknown'
            }
    
    @staticmethod
    def get_budget_alerts(user_id: int, by: str) -> List[Dict[str, Any]]:
        """
        Générer des alertes budget pour un utilisateur
        NOUVELLE FONCTIONNALITÉ débloquée par la migration !
        
        Args:
            user_id: ID de l'utilisateur
            by: Année fiscale format BYXX (ex: "BY25")
            
        Returns:
            Liste des alertes budget
        """
        try:
            consumption = UserBudgetModel.get_budget_consumption(user_id, by)
            alerts = []
            
            # Alerte dépassement budget
            if consumption['is_over_budget']:
                alerts.append({
                    'type': 'danger',
                    'title': 'Budget dépassé',
                    'message': f"Vous avez dépassé votre budget de {abs(consumption['remaining_budget']):,.0f}€",
                    'icon': '🚨'
                })
            
            # Alerte budget presque épuisé
            elif consumption['remaining_budget'] < consumption['allocated_budget'] * 0.1:  # <10% restant
                alerts.append({
                    'type': 'warning',
                    'title': 'Budget presque épuisé',
                    'message': f"Il ne vous reste que {consumption['remaining_budget']:,.0f}€ sur {consumption['allocated_budget']:,.0f}€",
                    'icon': '⚠️'
                })
            
            # Alerte consommation élevée
            elif consumption['consumption_rate'] > 80:
                alerts.append({
                    'type': 'info',
                    'title': 'Consommation élevée',
                    'message': f"Vous avez consommé {consumption['consumption_rate']:.1f}% de votre budget",
                    'icon': '📊'
                })
            
            # Alerte budget non utilisé
            elif consumption['consumption_rate'] < 10 and consumption['allocated_budget'] > 0:
                alerts.append({
                    'type': 'info',
                    'title': 'Budget peu utilisé',
                    'message': f"Vous n'avez utilisé que {consumption['consumption_rate']:.1f}% de votre budget",
                    'icon': '💡'
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Erreur génération alertes budget: {e}")
            return []
