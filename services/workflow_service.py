"""
Workflow service for managing demande approval workflow
"""
from typing import Dict, List, Any, Optional, Tuple
import logging

from models.demande import DemandeModel
from models.user import UserModel
from models.activity_log import ActivityLogModel
from services.notification_service import notification_service
from config.settings import WORKFLOW_CONFIG, has_permission

logger = logging.getLogger(__name__)

class WorkflowService:
    """Service for managing demande workflow"""
    
    @staticmethod
    def submit_demande(demande_id: int, user_id: int) -> Tuple[bool, str]:
        """Submit a demande for approval"""
        try:
            # Get demande and user info
            demande = DemandeModel.get_demande_by_id(demande_id)
            if not demande:
                return False, "Demande non trouvée"
            
            if demande['user_id'] != user_id:
                return False, "Vous n'êtes pas autorisé à soumettre cette demande"
            
            if demande['status'] != 'brouillon':
                return False, "Cette demande a déjà été soumise"
            
            user = UserModel.get_user_by_id(user_id)
            if not user:
                return False, "Utilisateur non trouvé"
            
            # Determine next status and validators
            next_status, validators = WorkflowService._get_next_workflow_step(
                demande['type_demande'], user['role'], user.get('directeur_id')
            )
            
            if not next_status:
                return False, "Workflow non défini pour ce type de demande et ce rôle"
            
            # Update demande status
            success = DemandeModel.update_demande(demande_id, status=next_status)
            if not success:
                return False, "Erreur lors de la mise à jour"
            
            # Log activity
            ActivityLogModel.log_activity(
                user_id, demande_id, 'soumission_demande',
                f"Soumission demande {demande['nom_manifestation']}"
            )
            
            # Send notifications to validators
            if validators:
                demande_info = {
                    'id': demande_id,
                    'nom_manifestation': demande['nom_manifestation'],
                    'client': demande['client'],
                    'montant': demande['montant'],
                    'type_demande': demande['type_demande'],
                    'user_nom': user['nom'],
                    'user_prenom': user['prenom']
                }
                
                notification_service.notify_demande_submitted(demande_info, validators)
            
            return True, "Demande soumise avec succès"
            
        except Exception as e:
            logger.error(f"Error submitting demande: {e}")
            return False, f"Erreur: {e}"
    
    @staticmethod
    def validate_demande(demande_id: int, validator_id: int, action: str, 
                        comment: str = "") -> Tuple[bool, str]:
        """Validate or reject a demande - Utilise le moteur centralisé"""
        try:
            from services.validation_engine import validation_engine
            return validation_engine.validate_demande(demande_id, validator_id, action, comment)
        except Exception as e:
            logger.error(f"Error validating demande via workflow service: {e}")
            return False, f"Erreur: {e}"
    
    @staticmethod
    def _get_next_workflow_step(demande_type: str, user_role: str, 
                               directeur_id: Optional[int]) -> Tuple[Optional[str], List[int]]:
        """Get next workflow step and validators"""
        try:
            workflow = WORKFLOW_CONFIG.get(demande_type, {})
            
            if demande_type == 'budget':
                if user_role == 'tc' and directeur_id:
                    return 'en_attente_dr', [directeur_id]
                elif user_role == 'dr':
                    # Get all financial validators
                    users_df = UserModel.get_all_users()
                    financiers = users_df[
                        users_df['role'].isin(['dr_financier', 'dg']) & 
                        users_df['is_active']
                    ]
                    return 'en_attente_financier', financiers['id'].tolist()
            
            elif demande_type == 'marketing':
                # Marketing goes directly to financial validation
                users_df = UserModel.get_all_users()
                validators = users_df[
                    users_df['role'].isin(['dr_financier', 'dg', 'admin']) & 
                    users_df['is_active']
                ]
                return 'en_attente_financier', validators['id'].tolist()
            
            return None, []
            
        except Exception as e:
            logger.error(f"Error getting workflow step: {e}")
            return None, []
    
    @staticmethod
    def _can_validate(demande: Dict[str, Any], validator: Dict[str, Any]) -> bool:
        """Check if validator can validate this demande"""
        try:
            validator_role = validator['role']
            demande_status = demande['status']
            
            if demande_status == 'en_attente_dr':
                # Only DR can validate at this stage
                if validator_role != 'dr':
                    return False
                
                # DR can only validate their team's demandes
                requester = UserModel.get_user_by_id(demande['user_id'])
                if requester and requester.get('directeur_id') == validator['id']:
                    return True
                
                # DR can validate their own demandes
                if demande['user_id'] == validator['id']:
                    return True
                
                return False
            
            elif demande_status == 'en_attente_financier':
                # Financial validators can validate
                return validator_role in ['dr_financier', 'dg', 'admin']
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking validation permission: {e}")
            return False
    
    @staticmethod
    def _process_validation(demande: Dict[str, Any], validator: Dict[str, Any], 
                           comment: str) -> Tuple[bool, str]:
        """Process demande validation"""
        try:
            current_status = demande['status']
            demande_id = demande['id']
            validator_id = validator['id']
            
            if current_status == 'en_attente_dr':
                # DR validation -> go to financial
                success = DemandeModel.update_demande(
                    demande_id,
                    status='en_attente_financier',
                    valideur_dr_id=validator_id,
                    commentaire_dr=comment
                )
                
                if success:
                    # Notify financial validators
                    users_df = UserModel.get_all_users()
                    financiers = users_df[
                        users_df['role'].isin(['dr_financier', 'dg']) & 
                        users_df['is_active']
                    ]
                    
                    for _, financier in financiers.iterrows():
                        notification_service.create_notification(
                            financier['id'], demande_id, 'demande_validation',
                            f"Demande validée par DR - {demande['nom_manifestation']}",
                            f"Une demande validée par le DR attend votre validation financière."
                        )
                    
                    # Notify requester
                    notification_service.notify_demande_validated(
                        demande, validator, 'dr'
                    )
                
                return success, "Demande validée et transmise aux financiers"
            
            elif current_status == 'en_attente_financier':
                # Financial validation -> final approval
                success = DemandeModel.update_demande(
                    demande_id,
                    status='validee',
                    valideur_financier_id=validator_id,
                    commentaire_financier=comment
                )
                
                if success:
                    # Notify requester and stakeholders
                    notification_service.notify_demande_validated(
                        demande, validator, 'final'
                    )
                
                return success, "Demande validée définitivement"
            
            return False, "Statut de demande non valide pour validation"
            
        except Exception as e:
            logger.error(f"Error processing validation: {e}")
            return False, f"Erreur lors de la validation: {e}"
    
    @staticmethod
    def _process_rejection(demande: Dict[str, Any], validator: Dict[str, Any], 
                          comment: str) -> Tuple[bool, str]:
        """Process demande rejection"""
        try:
            current_status = demande['status']
            demande_id = demande['id']
            validator_id = validator['id']
            
            if not comment.strip():
                return False, "Un motif de rejet est obligatoire"
            
            update_fields = {
                'status': 'rejetee'
            }
            
            if current_status == 'en_attente_dr':
                update_fields.update({
                    'valideur_dr_id': validator_id,
                    'commentaire_dr': comment
                })
            elif current_status == 'en_attente_financier':
                update_fields.update({
                    'valideur_financier_id': validator_id,
                    'commentaire_financier': comment
                })
            else:
                return False, "Statut de demande non valide pour rejet"
            
            success = DemandeModel.update_demande(demande_id, **update_fields)
            
            if success:
                # Notify requester
                notification_service.notify_demande_rejected(
                    demande, validator, comment
                )
            
            return success, "Demande rejetée"
            
        except Exception as e:
            logger.error(f"Error processing rejection: {e}")
            return False, f"Erreur lors du rejet: {e}"
    
    @staticmethod
    def get_pending_validations(user_id: int, user_role: str) -> Dict[str, Any]:
        """Get pending validations for a user"""
        try:
            pending = {'dr_validations': [], 'financial_validations': []}
            
            if user_role == 'dr':
                # Get demandes waiting for DR validation
                demandes_df = DemandeModel.get_demandes_for_user(user_id, user_role)
                dr_pending = demandes_df[demandes_df['status'] == 'en_attente_dr']
                pending['dr_validations'] = dr_pending.to_dict('records')
            
            elif user_role in ['dr_financier', 'dg', 'admin']:
                # Get demandes waiting for financial validation
                demandes_df = DemandeModel.get_demandes_for_user(user_id, user_role)
                fin_pending = demandes_df[demandes_df['status'] == 'en_attente_financier']
                pending['financial_validations'] = fin_pending.to_dict('records')
            
            return pending
            
        except Exception as e:
            logger.error(f"Error getting pending validations: {e}")
            return {'dr_validations': [], 'financial_validations': []}
    
    @staticmethod
    def get_workflow_history(demande_id: int) -> List[Dict[str, Any]]:
        """Get workflow history for a demande"""
        try:
            history_df = ActivityLogModel.get_demande_history(demande_id)
            return history_df.to_dict('records') if not history_df.empty else []
        except Exception as e:
            logger.error(f"Error getting workflow history: {e}")
            return []
    
    @staticmethod
    def can_user_edit_demande(demande_id: int, user_id: int) -> bool:
        """Check if user can edit a demande"""
        try:
            demande = DemandeModel.get_demande_by_id(demande_id)
            if not demande:
                return False
            
            # Only owner can edit
            if demande['user_id'] != user_id:
                return False
            
            # Only if in draft status
            return demande['status'] == 'brouillon'
            
        except Exception as e:
            logger.error(f"Error checking edit permission: {e}")
            return False
    
    @staticmethod
    def recall_demande(demande_id: int, user_id: int, reason: str) -> Tuple[bool, str]:
        """Recall a submitted demande back to draft"""
        try:
            demande = DemandeModel.get_demande_by_id(demande_id)
            if not demande:
                return False, "Demande non trouvée"
            
            if demande['user_id'] != user_id:
                return False, "Vous n'êtes pas autorisé à rappeler cette demande"
            
            if demande['status'] not in ['en_attente_dr', 'en_attente_financier']:
                return False, "Cette demande ne peut pas être rappelée"
            
            # Update status back to draft
            success = DemandeModel.update_demande(demande_id, status='brouillon')
            
            if success:
                # Log activity
                ActivityLogModel.log_activity(
                    user_id, demande_id, 'rappel_demande',
                    f"Rappel demande {demande['nom_manifestation']}: {reason}"
                )
                
                # Notify relevant validators that demande was recalled
                title = f"Demande rappelée - {demande['nom_manifestation']}"
                message = f"La demande a été rappelée par le demandeur. Motif: {reason}"
                
                # Get validators who were notified
                if demande['status'] == 'en_attente_dr' and demande.get('valideur_dr_id'):
                    notification_service.create_notification(
                        demande['valideur_dr_id'], demande_id, 'demande_rappel',
                        title, message, send_email=False
                    )
                elif demande['status'] == 'en_attente_financier':
                    users_df = UserModel.get_all_users()
                    financiers = users_df[
                        users_df['role'].isin(['dr_financier', 'dg']) & 
                        users_df['is_active']
                    ]
                    for _, financier in financiers.iterrows():
                        notification_service.create_notification(
                            financier['id'], demande_id, 'demande_rappel',
                            title, message, send_email=False
                        )
            
            return success, "Demande rappelée avec succès"
            
        except Exception as e:
            logger.error(f"Error recalling demande: {e}")
            return False, f"Erreur: {e}"
    
    @staticmethod
    def get_workflow_stats() -> Dict[str, Any]:
        """Get workflow statistics"""
        try:
            from models.demande import DemandeModel
            
            # Get all demandes
            all_demandes = DemandeModel.get_demandes_for_user(None, 'admin')
            
            if all_demandes.empty:
                return {
                    'total_demandes': 0,
                    'by_status': {},
                    'by_type': {},
                    'pending_validations': 0,
                    'average_processing_time': 0
                }
            
            stats = {
                'total_demandes': len(all_demandes),
                'by_status': all_demandes['status'].value_counts().to_dict(),
                'by_type': all_demandes['type_demande'].value_counts().to_dict(),
                'pending_validations': len(all_demandes[
                    all_demandes['status'].isin(['en_attente_dr', 'en_attente_financier'])
                ])
            }
            
            # Calculate average processing time for completed demandes
            completed = all_demandes[all_demandes['status'].isin(['validee', 'rejetee'])]
            if not completed.empty:
                completed['created_at'] = pd.to_datetime(completed['created_at'])
                completed['updated_at'] = pd.to_datetime(completed['updated_at'])
                processing_times = (completed['updated_at'] - completed['created_at']).dt.days
                stats['average_processing_time'] = processing_times.mean()
            else:
                stats['average_processing_time'] = 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting workflow stats: {e}")
            return {}

# Global workflow service instance
workflow_service = WorkflowService()
