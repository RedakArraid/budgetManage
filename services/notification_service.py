"""
Notification service for managing notifications and alerts
"""
from typing import List, Dict, Any, Optional
import logging

from models.notification import NotificationModel
from models.user import UserModel
from models.activity_log import ActivityLogModel
from services.email_service import email_service

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing notifications"""
    
    @staticmethod
    def create_notification(user_id: int, demande_id: Optional[int], 
                          notification_type: str, title: str, message: str,
                          send_email: bool = True) -> bool:
        """Create a new notification"""
        try:
            # Add to database
            success = NotificationModel.add_notification(
                user_id, demande_id, notification_type, title, message
            )
            
            if success and send_email:
                # Send email notification
                email_service.send_notification_email(user_id, title, message)
            
            return success
        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            return False
    
    @staticmethod
    def notify_demande_submitted(demande_info: Dict[str, Any], 
                               validators: List[int]) -> bool:
        """Notify validators when a demande is submitted"""
        try:
            title = f"Nouvelle demande à valider - {demande_info['nom_manifestation']}"
            message = f"""
            Une nouvelle demande de {demande_info['type_demande']} attend votre validation :
            
            • Manifestation : {demande_info['nom_manifestation']}
            • Client : {demande_info['client']}
            • Montant : {demande_info['montant']:,.0f}€
            • Demandeur : {demande_info['user_nom']} {demande_info['user_prenom']}
            """
            
            success_count = 0
            for validator_id in validators:
                if NotificationService.create_notification(
                    validator_id, demande_info['id'], 'demande_validation', title, message
                ):
                    success_count += 1
            
            return success_count > 0
        except Exception as e:
            logger.error(f"Error notifying demande submission: {e}")
            return False
    
    @staticmethod
    def notify_demande_validated(demande_info: Dict[str, Any], 
                               validator_info: Dict[str, Any],
                               validation_level: str) -> bool:
        """Notify when a demande is validated"""
        try:
            if validation_level == 'dr':
                title = f"Demande validée par DR - {demande_info['nom_manifestation']}"
                message = f"""
                Votre demande a été validée par le Directeur Régional {validator_info['nom']} {validator_info['prenom']}.
                Elle passe maintenant en validation financière.
                """
            else:  # final validation
                title = f"Demande validée définitivement - {demande_info['nom_manifestation']}"
                message = f"""
                Félicitations ! Votre demande a été validée définitivement par {validator_info['nom']} {validator_info['prenom']}.
                Vous pouvez maintenant procéder à l'organisation de votre événement.
                """
            
            # Notify the requester
            success = NotificationService.create_notification(
                demande_info['user_id'], demande_info['id'], 'demande_validee', title, message
            )
            
            # Also notify admins for final validations
            if validation_level == 'final':
                admin_users = UserModel.get_all_users()
                admin_ids = [u['id'] for _, u in admin_users.iterrows() if u['role'] == 'admin']
                
                for admin_id in admin_ids:
                    NotificationService.create_notification(
                        admin_id, demande_info['id'], 'demande_validee', 
                        f"Demande validée - {demande_info['nom_manifestation']}", 
                        f"La demande de {demande_info['user_nom']} {demande_info['user_prenom']} a été validée.", 
                        send_email=False
                    )
            
            return success
        except Exception as e:
            logger.error(f"Error notifying demande validation: {e}")
            return False
    
    @staticmethod
    def notify_demande_rejected(demande_info: Dict[str, Any], 
                              validator_info: Dict[str, Any],
                              rejection_reason: str) -> bool:
        """Notify when a demande is rejected"""
        try:
            title = f"Demande rejetée - {demande_info['nom_manifestation']}"
            message = f"""
            Votre demande a été rejetée par {validator_info['nom']} {validator_info['prenom']}.
            
            Motif du rejet : {rejection_reason}
            
            Vous pouvez créer une nouvelle demande en tenant compte de ces remarques.
            """
            
            return NotificationService.create_notification(
                demande_info['user_id'], demande_info['id'], 'demande_rejetee', title, message
            )
        except Exception as e:
            logger.error(f"Error notifying demande rejection: {e}")
            return False
    
    @staticmethod
    def notify_account_activation(user_id: int) -> bool:
        """Notify user when account is activated"""
        try:
            title = "Compte activé - Système de Gestion Budget"
            message = """
            Votre compte a été activé avec succès !
            
            Vous pouvez maintenant vous connecter au système de gestion budget.
            """
            
            return NotificationService.create_notification(
                user_id, None, 'account_activation', title, message
            )
        except Exception as e:
            logger.error(f"Error notifying account activation: {e}")
            return False
    
    @staticmethod
    def notify_system_maintenance(message: str, user_roles: List[str] = None) -> Dict[str, int]:
        """Notify users about system maintenance"""
        try:
            title = "Maintenance système prévue"
            
            users_df = UserModel.get_all_users()
            
            if user_roles:
                users_df = users_df[users_df['role'].isin(user_roles)]
            
            success_count = 0
            total_count = len(users_df)
            
            for _, user in users_df.iterrows():
                if user['is_active']:
                    if NotificationService.create_notification(
                        user['id'], None, 'system_maintenance', title, message, send_email=False
                    ):
                        success_count += 1
            
            return {'success': success_count, 'total': total_count}
        except Exception as e:
            logger.error(f"Error notifying system maintenance: {e}")
            return {'success': 0, 'total': 0}
    
    @staticmethod
    def send_reminders_pending_validations() -> Dict[str, int]:
        """Send reminders for pending validations"""
        try:
            from models.demande import DemandeModel
            
            # Get all pending demandes
            pending_dr = DemandeModel.get_demandes_for_user(None, 'admin')
            pending_dr = pending_dr[pending_dr['status'] == 'en_attente_dr']
            
            pending_financier = DemandeModel.get_demandes_for_user(None, 'admin')
            pending_financier = pending_financier[pending_financier['status'] == 'en_attente_financier']
            
            reminder_count = 0
            
            # Remind DRs
            dr_groups = pending_dr.groupby('directeur_id') if 'directeur_id' in pending_dr.columns else []
            for dr_id, group in dr_groups:
                if dr_id:
                    title = f"Rappel : {len(group)} demande(s) en attente de validation"
                    message = f"Vous avez {len(group)} demande(s) en attente de validation DR."
                    
                    if NotificationService.create_notification(
                        int(dr_id), None, 'reminder', title, message, send_email=False
                    ):
                        reminder_count += 1
            
            # Remind financiers
            if len(pending_financier) > 0:
                users_df = UserModel.get_all_users()
                financiers = users_df[users_df['role'].isin(['dr_financier', 'dg']) & users_df['is_active']]
                
                title = f"Rappel : {len(pending_financier)} demande(s) en attente de validation financière"
                message = f"Il y a {len(pending_financier)} demande(s) en attente de validation financière."
                
                for _, financier in financiers.iterrows():
                    if NotificationService.create_notification(
                        financier['id'], None, 'reminder', title, message, send_email=False
                    ):
                        reminder_count += 1
            
            return {'reminders_sent': reminder_count}
        except Exception as e:
            logger.error(f"Error sending reminders: {e}")
            return {'reminders_sent': 0}
    
    @staticmethod
    def cleanup_old_notifications(days: int = 30) -> int:
        """Clean up old notifications"""
        try:
            return NotificationModel.cleanup_old_notifications(days)
        except Exception as e:
            logger.error(f"Error cleaning up notifications: {e}")
            return 0
    
    @staticmethod
    def get_notification_summary(user_id: int) -> Dict[str, Any]:
        """Get notification summary for user"""
        try:
            unread_count = NotificationModel.get_unread_count(user_id)
            recent_notifications = NotificationModel.get_user_notifications(user_id, 5, unread_only=True)
            
            return {
                'unread_count': unread_count,
                'recent_notifications': recent_notifications.to_dict('records') if not recent_notifications.empty else []
            }
        except Exception as e:
            logger.error(f"Error getting notification summary: {e}")
            return {'unread_count': 0, 'recent_notifications': []}
    
    @staticmethod
    def mark_notifications_read(user_id: int, notification_ids: List[int] = None) -> bool:
        """Mark notifications as read"""
        try:
            if notification_ids:
                success = True
                for notif_id in notification_ids:
                    if not NotificationModel.mark_as_read(notif_id, user_id):
                        success = False
                return success
            else:
                return NotificationModel.mark_all_as_read(user_id)
        except Exception as e:
            logger.error(f"Error marking notifications as read: {e}")
            return False

# Global notification service instance
notification_service = NotificationService()
