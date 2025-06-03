"""
Moteur de validation centralisé pour toutes les demandes
Service unique pour gérer la logique de validation des demandes
"""
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime

from models.database import db
from config.settings import WORKFLOW_CONFIG, get_status_info

logger = logging.getLogger(__name__)

class ValidationEngine:
    """Moteur centralisé de validation des demandes"""
    
    @staticmethod
    def validate_demande(demande_id: int, validator_id: int, action: str, 
                        comment: str = "") -> Tuple[bool, str]:
        """
        Méthode centralisée pour valider ou rejeter une demande
        
        Args:
            demande_id: ID de la demande
            validator_id: ID du validateur
            action: 'valider' ou 'rejeter'
            comment: Commentaire de validation
            
        Returns:
            Tuple[bool, str]: (succès, message)
        """
        try:
            # Récupérer les informations de la demande et du validateur
            demande_info = ValidationEngine._get_demande_info(demande_id)
            if not demande_info:
                return False, "Demande non trouvée"
            
            validator_info = ValidationEngine._get_validator_info(validator_id)
            if not validator_info:
                return False, "Validateur non trouvé"

            # Debug: Afficher le rôle du validateur
            print(f"[DEBUG] ValidationEngine.validate_demande called by Valideur ID: {validator_id}, Role: {validator_info.get('role')}")
            
            # Vérifier les permissions de validation
            can_validate, permission_msg = ValidationEngine._check_validation_permission(
                demande_info, validator_info
            )
            if not can_validate:
                return False, permission_msg
            
            # Traiter l'action de validation
            if action == 'valider':
                return ValidationEngine._process_validation(demande_info, validator_info, comment)
            elif action == 'rejeter':
                return ValidationEngine._process_rejection(demande_info, validator_info, comment)
            else:
                return False, "Action non valide. Utilisez 'valider' ou 'rejeter'"
                
        except Exception as e:
            logger.error(f"Erreur lors de la validation de la demande {demande_id}: {e}")
            return False, f"Erreur technique: {str(e)}"
    
    @staticmethod
    def _get_demande_info(demande_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations complètes de la demande"""
        try:
            demande_data = db.execute_query('''
                SELECT d.*, u.nom as user_nom, u.prenom as user_prenom, 
                       u.email as user_email, u.role as user_role, u.directeur_id
                FROM demandes d
                JOIN users u ON d.user_id = u.id
                WHERE d.id = ?
            ''', (demande_id,), fetch='one')
            
            return dict(demande_data) if demande_data else None
        except Exception as e:
            logger.error(f"Erreur récupération demande {demande_id}: {e}")
            return None
    
    @staticmethod
    def _get_validator_info(validator_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer les informations du validateur"""
        try:
            validator_data = db.execute_query('''
                SELECT id, nom, prenom, email, role, region
                FROM users
                WHERE id = ? AND is_active = TRUE
            ''', (validator_id,), fetch='one')
            
            return dict(validator_data) if validator_data else None
        except Exception as e:
            logger.error(f"Erreur récupération validateur {validator_id}: {e}")
            return None
    
    @staticmethod
    def _check_validation_permission(demande_info: Dict[str, Any], 
                                   validator_info: Dict[str, Any]) -> Tuple[bool, str]:
        """Vérifier si le validateur peut valider cette demande"""
        try:
            validator_role = validator_info['role']
            validator_id = validator_info['id']
            demande_status = demande_info['status']
            demande_user_id = demande_info['user_id']
            directeur_id = demande_info.get('directeur_id')
            
            # Vérifications selon le statut de la demande
            if demande_status == 'en_attente_dr':
                # Seuls les DR peuvent valider à cette étape
                if validator_role != 'dr':
                    return False, "Seuls les Directeurs Régionaux peuvent valider à cette étape"
                
                # Le DR peut valider les demandes de son équipe ou ses propres demandes
                if validator_id == demande_user_id:
                    return True, "Validation de sa propre demande"
                elif validator_id == directeur_id:
                    return True, "Validation d'une demande de son équipe"
                else:
                    return False, "Vous ne pouvez valider que vos demandes ou celles de votre équipe"
            
            elif demande_status == 'en_attente_financier':
                # DR Financier, DG ou Admin peuvent valider
                if validator_role in ['dr_financier', 'dg', 'admin']:
                    return True, f"Validation financière par {validator_role}"
                else:
                    return False, "Seuls les validateurs financiers peuvent valider à cette étape"
            
            else:
                return False, f"Cette demande ne peut pas être validée (statut: {demande_status})"
                
        except Exception as e:
            logger.error(f"Erreur vérification permissions: {e}")
            return False, "Erreur lors de la vérification des permissions"
    
    @staticmethod
    def _process_validation(demande_info: Dict[str, Any], validator_info: Dict[str, Any], 
                          comment: str) -> Tuple[bool, str]:
        """Traiter une validation positive"""
        try:
            demande_id = demande_info['id']
            validator_id = validator_info['id']
            validator_role = validator_info['role']
            current_status = demande_info['status']
            
            # Déterminer les mises à jour selon le statut actuel
            if current_status == 'en_attente_dr':
                # Validation DR -> passage en attente financière
                update_fields = {
                    'status': 'en_attente_financier',
                    'valideur_dr_id': validator_id,
                    'date_validation_dr': datetime.now().isoformat(),
                    'commentaire_dr': comment or "Validé par le DR"
                }
                
                success = ValidationEngine._update_demande(demande_id, update_fields)
                if success:
                    # Notifier les validateurs financiers
                    ValidationEngine._notify_financial_validators(demande_info)
                    return True, "Demande validée par le DR et transmise aux financiers"
                else:
                    return False, "Erreur lors de la mise à jour de la demande"
            
            elif current_status == 'en_attente_financier':
                # Validation financière - gestion de la double validation
                return ValidationEngine._process_financial_validation(
                    demande_info, validator_info, comment
                )
            
            else:
                return False, f"Statut non valide pour validation: {current_status}"
                
        except Exception as e:
            logger.error(f"Erreur traitement validation: {e}")
            return False, f"Erreur lors du traitement: {str(e)}"
    
    @staticmethod
    def _process_financial_validation(demande_info: Dict[str, Any], 
                                    validator_info: Dict[str, Any], 
                                    comment: str) -> Tuple[bool, str]:
        """Traiter une validation financière (Financier/DG)"""
        try:
            demande_id = demande_info['id']
            validator_id = validator_info['id']
            validator_role = validator_info['role']
            
            # Récupérer l'état actuel des validations
            current_fin_validator = demande_info.get('valideur_financier_id')
            current_dg_validator = demande_info.get('valideur_dg_id')
            
            # Vérifier si le validateur a déjà validé
            if validator_role == 'dr_financier' and current_fin_validator == validator_id:
                return False, "Vous avez déjà validé cette demande en tant que Financier"
            if validator_role == 'dg' and current_dg_validator == validator_id:
                return False, "Vous avez déjà validé cette demande en tant que DG"
            
            # Préparer les mises à jour selon le rôle
            update_fields = {}
            
            if validator_role == 'dr_financier':
                update_fields.update({
                    'valideur_financier_id': validator_id,
                    'date_validation_financier': datetime.now().isoformat(),
                    'commentaire_financier': comment or "Validé par le Financier"
                })
                validation_type = "Financier"
                
            elif validator_role == 'dg':
                update_fields.update({
                    'valideur_dg_id': validator_id,
                    'date_validation_dg': datetime.now().isoformat(),
                    'commentaire_dg': comment or "Validé par le DG"
                })
                validation_type = "DG"
                
            elif validator_role == 'admin':
                # Admin peut valider comme financier ou DG selon ce qui manque
                if not current_fin_validator:
                    update_fields.update({
                        'valideur_financier_id': validator_id,
                        'date_validation_financier': datetime.now().isoformat(),
                        'commentaire_financier': comment or "Validé par l'Admin (Financier)"
                    })
                    validation_type = "Admin (Financier)"
                else:
                    update_fields.update({
                        'valideur_dg_id': validator_id,
                        'date_validation_dg': datetime.now().isoformat(),
                        'commentaire_dg': comment or "Validé par l'Admin (DG)"
                    })
                    validation_type = "Admin (DG)"
            
            # Déterminer si la demande est complètement validée
            fin_will_be_validated = (
                current_fin_validator is not None or 
                'valideur_financier_id' in update_fields
            )
            dg_will_be_validated = (
                current_dg_validator is not None or 
                'valideur_dg_id' in update_fields
            )
            
            if fin_will_be_validated and dg_will_be_validated:
                update_fields['status'] = 'validee'
                message = f"Demande validée par {validation_type} et finalement approuvée !"
            else:
                update_fields['status'] = 'en_attente_financier'  # Reste en attente
                missing = "DG" if fin_will_be_validated else "Financier"
                message = f"Demande validée par {validation_type}. En attente de validation par {missing}"
            
            # Mettre à jour la demande
            success = ValidationEngine._update_demande(demande_id, update_fields)
            if success:
                # Enregistrer la validation dans l'historique
                ValidationEngine._log_validation(demande_id, validator_id, 'valider', comment)
                
                # Notifier selon le statut final
                if update_fields['status'] == 'validee':
                    ValidationEngine._notify_final_approval(demande_info, validator_info)
                else:
                    ValidationEngine._notify_partial_approval(demande_info, validator_info, validation_type)
                
                return True, message
            else:
                return False, "Erreur lors de la mise à jour de la demande"
                
        except Exception as e:
            logger.error(f"Erreur validation financière: {e}")
            return False, f"Erreur lors de la validation financière: {str(e)}"
    
    @staticmethod
    def _process_rejection(demande_info: Dict[str, Any], validator_info: Dict[str, Any], 
                         comment: str) -> Tuple[bool, str]:
        """Traiter un rejet de demande"""
        try:
            if not comment.strip():
                return False, "Un motif de rejet est obligatoire"
            
            demande_id = demande_info['id']
            validator_id = validator_info['id']
            validator_role = validator_info['role']
            current_status = demande_info['status']
            
            # Préparer les mises à jour selon le statut
            update_fields = {'status': 'rejetee'}
            
            if current_status == 'en_attente_dr':
                update_fields.update({
                    'valideur_dr_id': validator_id,
                    'date_validation_dr': datetime.now().isoformat(),
                    'commentaire_dr': comment
                })
                rejection_level = "DR"
                
            elif current_status == 'en_attente_financier':
                if validator_role == 'dr_financier':
                    update_fields.update({
                        'valideur_financier_id': validator_id,
                        'date_validation_financier': datetime.now().isoformat(),
                        'commentaire_financier': comment
                    })
                    rejection_level = "Financier"
                    
                elif validator_role == 'dg':
                    update_fields.update({
                        'valideur_dg_id': validator_id,
                        'date_validation_dg': datetime.now().isoformat(),
                        'commentaire_dg': comment
                    })
                    rejection_level = "DG"
                    
                elif validator_role == 'admin':
                    update_fields.update({
                        'valideur_financier_id': validator_id,
                        'date_validation_financier': datetime.now().isoformat(),
                        'commentaire_financier': comment
                    })
                    rejection_level = "Admin"
            
            # Mettre à jour la demande
            success = ValidationEngine._update_demande(demande_id, update_fields)
            if success:
                # Enregistrer le rejet dans l'historique
                ValidationEngine._log_validation(demande_id, validator_id, 'rejeter', comment)
                
                # Notifier le rejet
                ValidationEngine._notify_rejection(demande_info, validator_info, comment)
                
                return True, f"Demande rejetée par {rejection_level}"
            else:
                return False, "Erreur lors de la mise à jour de la demande"
                
        except Exception as e:
            logger.error(f"Erreur traitement rejet: {e}")
            return False, f"Erreur lors du rejet: {str(e)}"
    
    @staticmethod
    def _update_demande(demande_id: int, update_fields: Dict[str, Any]) -> bool:
        """Mettre à jour une demande dans la base de données"""
        try:
            if not update_fields:
                return False
            
            # Construire la requête de mise à jour
            set_clauses = []
            values = []
            
            for key, value in update_fields.items():
                set_clauses.append(f"{key} = ?")
                values.append(value)
            
            # Toujours mettre à jour updated_at
            set_clauses.append("updated_at = CURRENT_TIMESTAMP")
            values.append(demande_id)
            
            query = f"UPDATE demandes SET {', '.join(set_clauses)} WHERE id = ?"
            
            db.execute_query(query, tuple(values))
            return True
            
        except Exception as e:
            logger.error(f"Erreur mise à jour demande {demande_id}: {e}")
            return False
    
    @staticmethod
    def _log_validation(demande_id: int, validator_id: int, action: str, comment: str):
        """Enregistrer une validation dans l'historique"""
        try:
            # Enregistrer dans demande_validations si la table existe
            try:
                db.execute_query('''
                    INSERT INTO demande_validations (demande_id, validated_by, validation_type, action, commentaire)
                    VALUES (?, ?, ?, ?, ?)
                ''', (demande_id, validator_id, 'general', action, comment))
            except:
                pass  # Table peut ne pas exister
            
            # Enregistrer dans activity_logs
            try:
                db.execute_query('''
                    INSERT INTO activity_logs (user_id, demande_id, action, details)
                    VALUES (?, ?, ?, ?)
                ''', (validator_id, demande_id, f'{action}_demande', comment))
            except:
                pass  # Table peut ne pas exister
                
        except Exception as e:
            logger.error(f"Erreur log validation: {e}")
    
    @staticmethod
    def _notify_financial_validators(demande_info: Dict[str, Any]):
        """Notifier les validateurs financiers qu'une demande est prête"""
        try:
            # Import local pour éviter les dépendances circulaires
            from services.notification_service import notification_service
            
            # Récupérer tous les validateurs financiers actifs
            validators = db.execute_query('''
                SELECT id, nom, prenom, email
                FROM users 
                WHERE role IN ('dr_financier', 'dg') AND is_active = TRUE
            ''', fetch='all')
            
            if validators:
                title = f"Nouvelle demande à valider - {demande_info['nom_manifestation']}"
                message = f"Une demande de {demande_info['user_prenom']} {demande_info['user_nom']} attend votre validation financière. Montant: {demande_info['montant']:,.0f}€"
                
                for validator in validators:
                    notification_service.create_notification(
                        validator['id'], demande_info['id'], 'demande_validation',
                        title, message
                    )
                    
        except Exception as e:
            logger.error(f"Erreur notification validateurs financiers: {e}")
    
    @staticmethod
    def _notify_final_approval(demande_info: Dict[str, Any], validator_info: Dict[str, Any]):
        """Notifier l'approbation finale de la demande"""
        try:
            from services.notification_service import notification_service
            
            # Notifier le demandeur
            title = f"Demande approuvée - {demande_info['nom_manifestation']}"
            message = f"Votre demande a été définitivement approuvée par {validator_info['prenom']} {validator_info['nom']}. Montant validé: {demande_info['montant']:,.0f}€"
            
            notification_service.create_notification(
                demande_info['user_id'], demande_info['id'], 'demande_approuvee',
                title, message, send_email=True
            )
            
        except Exception as e:
            logger.error(f"Erreur notification approbation finale: {e}")
    
    @staticmethod
    def _notify_partial_approval(demande_info: Dict[str, Any], validator_info: Dict[str, Any], validation_type: str):
        """Notifier une validation partielle"""
        try:
            from services.notification_service import notification_service
            
            # Notifier le demandeur de la validation partielle
            title = f"Demande validée partiellement - {demande_info['nom_manifestation']}"
            message = f"Votre demande a été validée par {validation_type} ({validator_info['prenom']} {validator_info['nom']}). En attente de la seconde validation."
            
            notification_service.create_notification(
                demande_info['user_id'], demande_info['id'], 'demande_validation_partielle',
                title, message, send_email=False
            )
            
        except Exception as e:
            logger.error(f"Erreur notification validation partielle: {e}")
    
    @staticmethod
    def _notify_rejection(demande_info: Dict[str, Any], validator_info: Dict[str, Any], comment: str):
        """Notifier le rejet de la demande"""
        try:
            from services.notification_service import notification_service
            
            # Notifier le demandeur du rejet
            title = f"Demande rejetée - {demande_info['nom_manifestation']}"
            message = f"Votre demande a été rejetée par {validator_info['prenom']} {validator_info['nom']}. Motif: {comment}"
            
            notification_service.create_notification(
                demande_info['user_id'], demande_info['id'], 'demande_rejetee',
                title, message, send_email=True
            )
            
        except Exception as e:
            logger.error(f"Erreur notification rejet: {e}")

# Instance globale du moteur de validation
validation_engine = ValidationEngine()
