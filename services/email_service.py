"""
Email service for sending notifications
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging

try:
    import win32com.client
    OUTLOOK_AVAILABLE = True
except ImportError:
    OUTLOOK_AVAILABLE = False

from config.settings import email_config
from models.user import UserModel

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications"""
    
    def __init__(self):
        self.config = email_config
    
    def send_email_outlook(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using Outlook COM"""
        if not OUTLOOK_AVAILABLE:
            logger.error("Outlook COM not available")
            return False
        
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            mail = outlook.CreateItem(0)
            mail.To = to_email
            mail.Subject = subject
            mail.HTMLBody = body
            mail.Send()
            return True
        except Exception as e:
            logger.error(f"Erreur envoi Outlook: {e}")
            return False
    
    def send_email_smtp(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.email
            msg['To'] = to_email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email, self.config.password)
            text = msg.as_string()
            server.sendmail(self.config.email, to_email, text)
            server.quit()
            
            return True
        except Exception as e:
            logger.error(f"Erreur envoi SMTP: {e}")
            return False
    
    def send_email(self, to_email: str, subject: str, body: str) -> bool:
        """Send email using preferred method"""
        if self.config.use_outlook and OUTLOOK_AVAILABLE:
            return self.send_email_outlook(to_email, subject, body)
        else:
            return self.send_email_smtp(to_email, subject, body)
    
    def send_notification_email(self, user_id: int, subject: str, message: str) -> bool:
        """Send notification email to a user"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            logger.error(f"User {user_id} not found")
            return False
        
        email_body = self._create_notification_template(
            user['prenom'], user['nom'], message
        )
        
        return self.send_email(user['email'], subject, email_body)
    
    def send_bulk_notification(self, user_ids: List[int], subject: str, message: str) -> dict:
        """Send notification to multiple users"""
        results = {
            'success': [],
            'failed': []
        }
        
        for user_id in user_ids:
            if self.send_notification_email(user_id, subject, message):
                results['success'].append(user_id)
            else:
                results['failed'].append(user_id)
        
        return results
    
    def send_account_activation_email(self, user_id: int, temporary_password: str = None) -> bool:
        """Send account activation email"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return False
        
        subject = "Activation de votre compte - Système de Gestion Budget"
        
        if temporary_password:
            message = f"""
            Votre compte a été créé avec succès !
            
            Votre mot de passe temporaire est : {temporary_password}
            
            Veuillez vous connecter et changer votre mot de passe lors de votre première connexion.
            """
        else:
            message = "Votre compte a été activé. Vous pouvez maintenant vous connecter au système."
        
        return self.send_notification_email(user_id, subject, message)
    
    def send_demande_notification(self, user_id: int, demande_info: dict, 
                                action: str, validator_name: str = "") -> bool:
        """Send demande-related notification"""
        action_messages = {
            'submitted': f"Votre demande '{demande_info['nom_manifestation']}' a été soumise pour validation.",
            'validated_dr': f"Votre demande '{demande_info['nom_manifestation']}' a été validée par le DR {validator_name}.",
            'validated_final': f"Félicitations ! Votre demande '{demande_info['nom_manifestation']}' a été validée définitivement.",
            'rejected': f"Votre demande '{demande_info['nom_manifestation']}' a été rejetée.",
            'needs_validation': f"Une nouvelle demande '{demande_info['nom_manifestation']}' attend votre validation."
        }
        
        subject_map = {
            'submitted': "Demande soumise",
            'validated_dr': "Demande validée par DR",
            'validated_final': "Demande validée - Félicitations !",
            'rejected': "Demande rejetée",
            'needs_validation': "Nouvelle demande à valider"
        }
        
        message = action_messages.get(action, "Notification concernant votre demande")
        subject = subject_map.get(action, "Notification - Système Budget")
        
        return self.send_notification_email(user_id, subject, message)
    
    def send_password_reset_email(self, user_id: int, reset_token: str) -> bool:
        """Send password reset email"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return False
        
        subject = "Réinitialisation de mot de passe - Système Budget"
        message = f"""
        Une demande de réinitialisation de mot de passe a été effectuée pour votre compte.
        
        Code de réinitialisation : {reset_token}
        
        Ce code expire dans 24 heures.
        
        Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
        """
        
        return self.send_notification_email(user_id, subject, message)
    
    def send_weekly_summary(self, user_id: int, summary_data: dict) -> bool:
        """Send weekly summary email"""
        user = UserModel.get_user_by_id(user_id)
        if not user:
            return False
        
        subject = "Résumé hebdomadaire - Système Budget"
        
        message = f"""
        Voici votre résumé d'activité de la semaine :
        
        • Demandes créées : {summary_data.get('created', 0)}
        • Demandes validées : {summary_data.get('validated', 0)}
        • Montant total validé : {summary_data.get('total_amount', 0):,.0f}€
        
        Notifications en attente : {summary_data.get('pending_notifications', 0)}
        """
        
        return self.send_notification_email(user_id, subject, message)
    
    def _create_notification_template(self, prenom: str, nom: str, message: str) -> str:
        """Create HTML email template"""
        return f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #4CAF50, #45a049); color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ background-color: #333; color: white; padding: 10px; text-align: center; font-size: 12px; }}
                .button {{ background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>💰 Système de Gestion Budget</h1>
            </div>
            <div class="content">
                <h2>Bonjour {prenom} {nom},</h2>
                <p>{message}</p>
                <p>Pour accéder au système, <a href="#" class="button">Cliquez ici</a></p>
            </div>
            <div class="footer">
                <p>Ceci est un message automatique du système de gestion budget.</p>
                <p>Ne pas répondre à cet email.</p>
            </div>
        </body>
        </html>
        """
    
    def test_email_configuration(self) -> tuple[bool, str]:
        """Test email configuration"""
        try:
            if self.config.use_outlook and OUTLOOK_AVAILABLE:
                # Test Outlook connection
                outlook = win32com.client.Dispatch("Outlook.Application")
                return True, "Configuration Outlook OK"
            else:
                # Test SMTP connection
                server = smtplib.SMTP(self.config.smtp_server, self.config.smtp_port)
                server.starttls()
                server.login(self.config.email, self.config.password)
                server.quit()
                return True, "Configuration SMTP OK"
        except Exception as e:
            return False, f"Erreur de configuration: {e}"

# Global email service instance
email_service = EmailService()
