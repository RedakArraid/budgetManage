"""
User controller for CRUD operations - VERSION CORRIGÉE
"""
import streamlit as st
from typing import Optional, Dict, Any, List, Tuple
import pandas as pd

from models.user import UserModel
from models.activity_log import ActivityLogModel
from controllers.auth_controller import AuthController
from utils.validators import validate_email, validate_password, validate_text_field
from config.settings import role_config

class UserController:
    """Controller for user operations"""
    
    @staticmethod
    def create_user(email: str, nom: str, prenom: str, role: str, region: str = None, 
                   directeur_id: int = None, budget_alloue: float = 0.0) -> Tuple[bool, str]:
        """Create a new user"""
        try:
            # Validation des champs
            if not validate_email(email):
                return False, "Format d'email invalide"
            
            if not validate_text_field(nom, min_length=2):
                return False, "Le nom doit contenir au moins 2 caractères"
            
            if not validate_text_field(prenom, min_length=2):
                return False, "Le prénom doit contenir au moins 2 caractères"
            
            if role not in role_config.roles:
                return False, "Rôle invalide"
            
            # Règles spécifiques par rôle
            if role == 'dr' and not region:
                return False, "Une région doit être sélectionnée pour un DR"
            
            if role == 'tc' and not directeur_id:
                return False, "Un directeur doit être sélectionné pour un TC"
            
            # Si c'est un TC, récupérer la région du DR
            if role == 'tc' and directeur_id:
                dr_info = UserModel.get_user_by_id(directeur_id)
                if not dr_info:
                    return False, "Directeur introuvable"
                if dr_info['role'] != 'dr':
                    return False, "Le directeur sélectionné n'est pas un DR"
                region = dr_info['region']  # Région automatique du DR
            
            # Générer un mot de passe temporaire
            temp_password = "TempPass123!"  # À changer à la première connexion
            
            # Créer l'utilisateur
            success, user_id = UserModel.create_user(
                email=email,
                nom=nom,
                prenom=prenom,
                role=role,
                region=region,
                directeur_id=directeur_id,
                budget_alloue=budget_alloue,
                temp_password=temp_password
            )
            
            if success:
                # Log de l'activité
                current_user_id = AuthController.get_current_user_id()
                ActivityLogModel.log_activity(
                    current_user_id, None, 'create_user',
                    f"Création utilisateur {email} ({role})"
                )
                
                return True, f"Utilisateur créé avec succès. Mot de passe temporaire: {temp_password}"
            else:
                return False, "Erreur lors de la création de l'utilisateur"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            return UserModel.get_user_by_id(user_id)
        except Exception as e:
            st.error(f"Erreur lors de la récupération de l'utilisateur: {e}")
            return None
    
    @staticmethod
    def change_password(user_id: int, new_password: str) -> bool:
        """Change user password"""
        try:
            from utils.security import hash_password
            password_hash = hash_password(new_password)
            
            success = UserModel.update_user(user_id, password_hash=password_hash)
            
            if success:
                # Log de l'activité
                user_info = UserModel.get_user_by_id(user_id)
                ActivityLogModel.log_activity(
                    user_id, None, 'change_password',
                    f"Changement de mot de passe pour {user_info['email'] if user_info else user_id}"
                )
                
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    @staticmethod
    def update_user_profile(user_id: int, prenom: str, nom: str, region: str = None) -> bool:
        """Update user profile information"""
        try:
            # Préparer les données à mettre à jour
            update_data = {
                'prenom': prenom,
                'nom': nom
            }
            
            if region:
                update_data['region'] = region
            
            success = UserModel.update_user(user_id, **update_data)
            
            if success:
                # Log de l'activité
                user_info = UserModel.get_user_by_id(user_id)
                ActivityLogModel.log_activity(
                    user_id, None, 'update_profile',
                    f"Mise à jour du profil pour {user_info['email'] if user_info else user_id}"
                )
                
                return True
            else:
                return False
                
        except Exception as e:
            return False
    
    @staticmethod
    def reset_password(user_id: int) -> Tuple[bool, str]:
        """Reset user password"""
        try:
            new_password = "NewPass123!"
            success = UserModel.reset_password(user_id, new_password)
            
            if success:
                # Log de l'activité
                current_user_id = AuthController.get_current_user_id()
                user_info = UserModel.get_user_by_id(user_id)
                ActivityLogModel.log_activity(
                    current_user_id, None, 'reset_password',
                    f"Réinitialisation mot de passe {user_info['email'] if user_info else user_id}"
                )
                
                return True, f"Mot de passe réinitialisé: {new_password}"
            else:
                return False, "Erreur lors de la réinitialisation"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def get_all_users(search_query: str = "", role_filter: str = "tous", 
                     status_filter: str = "tous") -> pd.DataFrame:
        """Get all users with filters"""
        try:
            users_df = UserModel.get_all_users()
            
            if users_df.empty:
                return pd.DataFrame()
            
            # Filtres
            if search_query:
                mask = (
                    users_df['nom'].str.contains(search_query, case=False, na=False) |
                    users_df['prenom'].str.contains(search_query, case=False, na=False) |
                    users_df['email'].str.contains(search_query, case=False, na=False)
                )
                users_df = users_df[mask]
            
            if role_filter != "tous":
                users_df = users_df[users_df['role'] == role_filter]
            
            if status_filter == "actifs":
                users_df = users_df[users_df['is_active'] == True]
            elif status_filter == "inactifs":
                users_df = users_df[users_df['is_active'] == False]
            
            return users_df
            
        except Exception as e:
            st.error(f"Erreur lors de la récupération des utilisateurs: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> Tuple[bool, str]:
        """Update user information"""
        try:
            success = UserModel.update_user(user_id, **kwargs)
            
            if success:
                # Log de l'activité
                current_user_id = AuthController.get_current_user_id()
                user_info = UserModel.get_user_by_id(user_id)
                ActivityLogModel.log_activity(
                    current_user_id, None, 'update_user',
                    f"Modification utilisateur {user_info['email'] if user_info else user_id}"
                )
                
                return True, "Utilisateur mis à jour avec succès"
            else:
                return False, "Erreur lors de la mise à jour"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def activate_user(user_id: int, activate: bool = True) -> Tuple[bool, str]:
        """Activate or deactivate a user"""
        try:
            success = UserModel.update_user(user_id, is_active=activate)
            
            if success:
                # Log de l'activité
                current_user_id = AuthController.get_current_user_id()
                user_info = UserModel.get_user_by_id(user_id)
                action = 'activate_user' if activate else 'deactivate_user'
                status = 'activé' if activate else 'désactivé'
                
                ActivityLogModel.log_activity(
                    current_user_id, None, action,
                    f"Utilisateur {user_info['email'] if user_info else user_id} {status}"
                )
                
                return True, f"Utilisateur {'activé' if activate else 'désactivé'} avec succès"
            else:
                return False, "Erreur lors de la modification du statut"
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, str]:
        """Delete a user (soft delete by deactivating)"""
        try:
            # Vérifier que ce n'est pas le dernier admin
            if UserModel.is_last_admin(user_id):
                return False, "Impossible de supprimer le dernier administrateur"
            
            # Vérifier que l'utilisateur n'a pas de demandes en cours
            if UserModel.has_pending_requests(user_id):
                return False, "Impossible de supprimer un utilisateur avec des demandes en cours"
            
            # Désactiver l'utilisateur au lieu de le supprimer
            success, message = UserController.activate_user(user_id, activate=False)
            
            if success:
                return True, "Utilisateur supprimé (désactivé) avec succès"
            else:
                return False, message
                
        except Exception as e:
            return False, f"Erreur: {str(e)}"
    
    @staticmethod
    def get_directors() -> List[Dict[str, Any]]:
        """Get all directors (DR) for TC assignment"""
        try:
            return UserModel.get_users_by_role('dr', active_only=True)
        except Exception as e:
            st.error(f"Erreur lors de la récupération des directeurs: {e}")
            return []
    
    @staticmethod
    def get_regions() -> List[str]:
        """Get all available regions"""
        try:
            from models.dropdown_options import DropdownOptionsModel
            regions = DropdownOptionsModel.get_options_by_category('region')
            return [region['value'] for region in regions]
        except Exception as e:
            st.error(f"Erreur lors de la récupération des régions: {e}")
            return []
    
    @staticmethod
    def get_user_statistics() -> Dict[str, Any]:
        """Get user statistics for admin dashboard"""
        try:
            stats = {}
            
            # Total users
            all_users = UserModel.get_all_users()
            stats['total_users'] = len(all_users)
            stats['active_users'] = len(all_users[all_users['is_active'] == True])
            stats['inactive_users'] = len(all_users[all_users['is_active'] == False])
            
            # By role
            role_counts = all_users['role'].value_counts().to_dict()
            stats['by_role'] = role_counts
            
            # By region
            region_counts = all_users['region'].value_counts().to_dict()
            stats['by_region'] = region_counts
            
            return stats
            
        except Exception as e:
            st.error(f"Erreur lors du calcul des statistiques: {e}")
            return {}
    
    @staticmethod
    def export_users() -> pd.DataFrame:
        """Export users data for Excel/CSV"""
        try:
            users_df = UserModel.get_all_users()
            
            if users_df.empty:
                return pd.DataFrame()
            
            # Sélectionner et renommer les colonnes pour l'export
            export_df = users_df[['id', 'email', 'nom', 'prenom', 'role', 'region', 
                                'budget_alloue', 'is_active', 'created_at']].copy()
            
            export_df.columns = ['ID', 'Email', 'Nom', 'Prénom', 'Rôle', 'Région', 
                               'Budget Alloué', 'Actif', 'Date Création']
            
            # Formater les données
            export_df['Budget Alloué'] = export_df['Budget Alloué'].apply(lambda x: f"{x:,.2f}€")
            export_df['Actif'] = export_df['Actif'].apply(lambda x: 'Oui' if x else 'Non')
            export_df['Date Création'] = pd.to_datetime(export_df['Date Création']).dt.strftime('%d/%m/%Y')
            
            # Traduire les rôles
            from config.settings import get_role_label
            export_df['Rôle'] = export_df['Rôle'].apply(get_role_label)
            
            return export_df
            
        except Exception as e:
            st.error(f"Erreur lors de l'export: {e}")
            return pd.DataFrame()
