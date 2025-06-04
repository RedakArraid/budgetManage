"""
Contrôleur pour les demandes
"""
from typing import Optional, List, Dict, Any, Tuple
import pandas as pd
from models.demande import DemandeModel
from models.activity_log import ActivityLogModel
from models.database import db
from datetime import datetime

class DemandeController:
    """Contrôleur pour la gestion des demandes"""
    
    @staticmethod
    def create_demande(user_id: int, type_demande: str, nom_manifestation: str, 
                      client: str, date_evenement: str, lieu: str, montant: float, 
                      participants: str = "", commentaires: str = "", urgence: str = "normale",
                      budget: str = "", categorie: str = "", typologie_client: str = "",
                      groupe_groupement: str = "", region: str = "", agence: str = "",
                      client_enseigne: str = "", mail_contact: str = "", nom_contact: str = "",
                      demandeur_participe: bool = True, participants_libres: str = "",
                      selected_participants: List[int] = None) -> Tuple[bool, Optional[int]]:
        """Créer une nouvelle demande avec gestion des participants ET validation centralisée"""
        
        print(f"[DEBUG] create_demande called by user_id: {user_id} with type: {type_demande}")
        print(f"[DEBUG] Nom manifestation: {nom_manifestation}, Client: {client}, Montant: {montant}")
        
        # VALIDATION OBLIGATOIRE via le système centralisé
        from utils.dropdown_manager import DropdownSecurityLayer
        
        demande_data = {
            'budget': budget,
            'categorie': categorie,
            'typologie_client': typologie_client,
            'groupe_groupement': groupe_groupement,
            'region': region
        }
        
        # Vérifier que toutes les valeurs sont autorisées
        is_valid, validated_data, errors = DropdownSecurityLayer.secure_demande_creation(demande_data)
        
        if not is_valid:
            error_msg = "Valeurs non autorisées détectées: " + "; ".join(errors)
            print(f"❌ {error_msg}")
            return False, None
        
        # Créer la demande via le modèle
        success, demande_id = DemandeModel.create_demande(
            user_id=user_id,
            type_demande=type_demande,
            nom_manifestation=nom_manifestation,
            client=client,
            date_evenement=date_evenement,
            lieu=lieu,
            montant=montant,
            participants=participants,
            commentaires=commentaires,
            urgence=urgence,
            budget=budget,
            categorie=categorie,
            typologie_client=typologie_client,
            groupe_groupement=groupe_groupement,
            region=region,
            agence=agence,
            client_enseigne=client_enseigne,
            mail_contact=mail_contact,
            nom_contact=nom_contact,
            demandeur_participe=demandeur_participe,
            participants_libres=participants_libres
        )
        
        if success and demande_id:
            # Logger l'activité
            ActivityLogModel.log_activity(
                user_id, demande_id, 'creation_demande',
                f"Création demande '{nom_manifestation}' - {montant}€"
            )
            
            # Gérer les participants selon le rôle
            from models.participant import ParticipantModel
            from models.user import UserModel
            
            # Récupérer le rôle de l'utilisateur
            user_data = UserModel.get_user_by_id(user_id)
            if user_data:
                user_role = user_data['role']
                
                # Logique selon le rôle
                if user_role == 'tc':
                    # TC participe automatiquement
                    ParticipantModel.add_participant(demande_id, user_id, user_id)
                    
                elif user_role == 'dr':
                    # DR peut choisir de participer
                    if demandeur_participe:
                        ParticipantModel.add_participant(demande_id, user_id, user_id)
                    
                # Ajouter les participants sélectionnés (TCs pour DR)
                if selected_participants:
                    for selected_participant_id in selected_participants:
                        ParticipantModel.add_participant(demande_id, selected_participant_id, user_id)
            
            # Gérer la validation automatique pour les DR créateurs
            if user_data and user_data['role'] == 'dr':
                 now = datetime.now().isoformat()
                 # Mettre à jour le statut et les champs de validation DR
                 update_success = DemandeModel.update_demande(
                      demande_id,
                      status='en_attente_financier', # Passer directement à l'étape suivante
                      valideur_dr_id=user_id,
                      date_validation_dr=now,
                      commentaire_dr="Validée automatiquement par le créateur (DR)"
                 )
                 if not update_success:
                      print(f"[WARNING] Failed to auto-validate DR demand {demande_id}")
        
        print(f"[DEBUG] create_demande returning success: {success}, demande_id: {demande_id}")
        return success, demande_id
    
    @staticmethod
    def get_demandes_for_user(user_id: int, role: str, search_query: str = "", 
                             status_filter: str = "tous") -> pd.DataFrame:
        """Récupérer les demandes pour un utilisateur selon son rôle"""
        return DemandeModel.get_demandes_for_user(user_id, role, search_query, status_filter)
    
    @staticmethod
    def get_demande_by_id(demande_id: int) -> Optional[Dict[str, Any]]:
        """Récupérer une demande par son ID"""
        return DemandeModel.get_demande_by_id(demande_id)
    
    @staticmethod
    def update_demande(demande_id: int, **kwargs) -> bool:
        """Mettre à jour une demande avec validation centralisée"""
        
        # VALIDATION OBLIGATOIRE pour les champs dropdown
        from utils.dropdown_manager import DropdownSecurityLayer
        
        is_valid, validated_data, errors = DropdownSecurityLayer.secure_demande_update(demande_id, kwargs)
        
        if not is_valid:
            error_msg = "Valeurs non autorisées détectées: " + "; ".join(errors)
            print(f"❌ Mise à jour rejetée - {error_msg}")
            return False
        
        return DemandeModel.update_demande(demande_id, **kwargs)
    
    @staticmethod
    def submit_demande(demande_id: int, user_id: int) -> Tuple[bool, str]:
        """Soumettre une demande pour validation"""
        
        # Soumettre via le modèle
        success, message = DemandeModel.submit_demande(demande_id, user_id)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                user_id, demande_id, 'soumission_demande',
                f"Soumission demande pour validation"
            )
        
        return success, message
    
    @staticmethod
    def validate_demande(demande_id: int, valideur_id: int, action: str, 
                        commentaire: str = "") -> Tuple[bool, str]:
        """Valider ou rejeter une demande"""
        
        # Valider via le modèle
        success, message = DemandeModel.validate_demande(demande_id, valideur_id, action, commentaire)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                valideur_id, demande_id, f'{action}_demande',
                f"Demande {action}ée - Commentaire: {commentaire}"
            )
        
        return success, message
    
    @staticmethod
    def get_dashboard_stats(user_id: int, role: str) -> Dict[str, Any]:
        """Récupérer les statistiques pour le tableau de bord"""
        return DemandeModel.get_dashboard_stats(user_id, role)
    
    @staticmethod
    def get_analytics_data(user_id: int, role: str) -> Dict[str, Any]:
        """Récupérer les données d'analyse"""
        return DemandeModel.get_analytics_data(user_id, role)
    
    @staticmethod
    def delete_demande(demande_id: int, user_id: int) -> bool:
        """Supprimer une demande (uniquement si brouillon et propriétaire)"""
        
        success = DemandeModel.delete_demande(demande_id, user_id)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                user_id, demande_id, 'suppression_demande',
                f"Suppression demande brouillon"
            )
        
        return success
    
    @staticmethod
    def get_validation_pending_count(user_id: int, role: str) -> int:
        """Récupérer le nombre de demandes en attente de validation pour un utilisateur"""
        try:
            if role == 'dr':
                # Pour un DR, compter les demandes de son équipe en attente de validation DR
                demandes = DemandeModel.get_demandes_for_user(user_id, role, status_filter='en_attente_dr')
                return len(demandes)
            elif role in ['dr_financier', 'dg']:
                # Pour les financiers, compter les demandes en attente de validation financière
                demandes = DemandeModel.get_demandes_for_user(user_id, role, status_filter='en_attente_financier')
                return len(demandes)
            else:
                return 0
        except Exception:
            return 0
    
    @staticmethod
    def get_demandes_summary(user_id: int, role: str) -> Dict[str, Any]:
        """Récupérer un résumé des demandes pour l'utilisateur"""
        try:
            demandes = DemandeModel.get_demandes_for_user(user_id, role)
            
            if demandes.empty:
                return {
                    'total': 0,
                    'brouillon': 0,
                    'en_cours': 0,
                    'validees': 0,
                    'rejetees': 0,
                    'montant_total': 0
                }
            
            # Calculer les statistiques
            summary = {
                'total': len(demandes),
                'brouillon': len(demandes[demandes['status'] == 'brouillon']),
                'en_cours': len(demandes[demandes['status'].isin(['en_attente_dr', 'en_attente_financier'])]),
                'validees': len(demandes[demandes['status'] == 'validee']),
                'rejetees': len(demandes[demandes['status'] == 'rejetee']),
                'montant_total': demandes['montant'].sum(),
                'montant_valide': demandes[demandes['status'] == 'validee']['montant'].sum()
            }
            
            return summary
            
        except Exception as e:
            print(f"Erreur résumé demandes: {e}")
            return {}
    
    @staticmethod
    def add_participant_to_demande(demande_id: int, participant_id: int, added_by_user_id: int) -> bool:
        """Ajouter un participant à une demande existante"""
        from models.participant import ParticipantModel
        
        success = ParticipantModel.add_participant(demande_id, participant_id, added_by_user_id)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                added_by_user_id, demande_id, 'ajout_participant',
                f"Ajout participant ID {participant_id}"
            )
        
        return success
    
    @staticmethod
    def remove_participant_from_demande(demande_id: int, participant_id: int, removed_by_user_id: int) -> bool:
        """Supprimer un participant d'une demande"""
        from models.participant import ParticipantModel
        
        success = ParticipantModel.remove_participant(demande_id, participant_id)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                removed_by_user_id, demande_id, 'suppression_participant',
                f"Suppression participant ID {participant_id}"
            )
        
        return success
    
    @staticmethod
    def get_participants_summary(demande_id: int) -> Dict[str, Any]:
        """Récupérer un résumé des participants d'une demande"""
        from models.participant import ParticipantModel
        return ParticipantModel.get_participant_summary(demande_id)
    
    @staticmethod
    def get_available_participants_for_user(user_id: int, user_role: str) -> List[Dict[str, Any]]:
        """Récupérer la liste des participants disponibles selon le rôle"""
        from models.user import UserModel
        
        if user_role == 'dr':
            # DR peut sélectionner ses TCs
            return UserModel.get_tc_users_by_director(user_id)
        elif user_role == 'admin':
            # Admin peut sélectionner tous les TCs
            return UserModel.get_all_tc_users()
        else:
            # Autres rôles n'ont pas accès à la sélection
            return []
    
    @staticmethod
    def get_validation_stats(user_id: int, role: str) -> Dict[str, Any]:
        """Récupérer les statistiques de validation pour un utilisateur"""
        try:
            from datetime import datetime, timedelta
            
            stats = {
                'total_validees': 0,
                'ce_mois': 0,
                'montant_valide': 0,
                'temps_moyen': 0
            }
            
            # Calculer le début du mois
            debut_mois = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if role == 'dr':
                # Statistiques pour DR
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Total validées par ce DR
                    cursor.execute("""
                        SELECT COUNT(*), COALESCE(SUM(montant), 0)
                        FROM demandes 
                        WHERE valideur_dr_id = ? AND status IN ('en_attente_financier', 'validee')
                    """, (user_id,))
                    total_result = cursor.fetchone()
                    stats['total_validees'] = total_result[0] if total_result else 0
                    stats['montant_valide'] = total_result[1] if total_result else 0
                    
                    # Ce mois
                    cursor.execute("""
                        SELECT COUNT(*)
                        FROM demandes 
                        WHERE valideur_dr_id = ? 
                        AND date_validation_dr >= ?
                        AND status IN ('en_attente_financier', 'validee')
                    """, (user_id, debut_mois.isoformat()))
                    mois_result = cursor.fetchone()
                    stats['ce_mois'] = mois_result[0] if mois_result else 0
                    
            elif role in ['dr_financier', 'dg']:
                # Statistiques pour financiers/DG
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    
                    # Champ de validation selon le rôle
                    if role == 'dr_financier':
                        valideur_field = 'valideur_financier_id'
                        date_field = 'date_validation_financier'
                    else:  # dg
                        valideur_field = 'valideur_dg_id'
                        date_field = 'date_validation_dg'
                    
                    # Total validées
                    cursor.execute(f"""
                        SELECT COUNT(*), COALESCE(SUM(montant), 0)
                        FROM demandes 
                        WHERE {valideur_field} = ? AND status = 'validee'
                    """, (user_id,))
                    total_result = cursor.fetchone()
                    stats['total_validees'] = total_result[0] if total_result else 0
                    stats['montant_valide'] = total_result[1] if total_result else 0
                    
                    # Ce mois
                    cursor.execute(f"""
                        SELECT COUNT(*)
                        FROM demandes 
                        WHERE {valideur_field} = ? 
                        AND {date_field} >= ?
                        AND status = 'validee'
                    """, (user_id, debut_mois.isoformat()))
                    mois_result = cursor.fetchone()
                    stats['ce_mois'] = mois_result[0] if mois_result else 0
            
            # Calculer temps moyen (estimation simple)
            if stats['total_validees'] > 0:
                stats['temps_moyen'] = 24.0  # Estimation: 24h en moyenne
            
            return stats
            
        except Exception as e:
            print(f"Erreur stats validation: {e}")
            return {
                'total_validees': 0,
                'ce_mois': 0,
                'montant_valide': 0,
                'temps_moyen': 0
            }
    
    @staticmethod
    def permanently_delete_demande(demande_id: int) -> Tuple[bool, str]:
        """Supprimer définitivement une demande (utilisé par l'admin)"""
        try:
            # Vérifier si la demande existe
            demande = DemandeModel.get_demande_by_id(demande_id)
            if not demande:
                return False, "Demande non trouvée."

            # Supprimer les participants liés
            db.execute_query('DELETE FROM demande_participants WHERE demande_id = ?', (demande_id,))

            # Supprimer les logs d'activité liés
            db.execute_query('DELETE FROM activity_log WHERE demande_id = ?', (demande_id,))

            # Supprimer la demande elle-même
            db.execute_query('DELETE FROM demandes WHERE id = ?', (demande_id,))

            return True, "Demande supprimée avec succès."
        except Exception as e:
            print(f"Erreur suppression définitive demande: {e}")
            return False, f"Erreur lors de la suppression de la demande: {e}"
    
    @staticmethod
    def get_demande_dependencies(demande_id: int) -> Dict[str, int]:
        """Get demande dependencies before deletion"""
        try:
            from models.demande import DemandeModel
            return DemandeModel.get_demande_dependencies(demande_id)
        except Exception as e:
            return {}
    
    @staticmethod
    def admin_delete_demande(demande_id: int, admin_user_id: int) -> Tuple[bool, str]:
        """Permet à un administrateur de supprimer définitivement une demande"""
        from models.user import UserModel
        
        # Vérifier que l'utilisateur est bien un admin
        admin_user = UserModel.get_user_by_id(admin_user_id)
        if not admin_user or admin_user['role'] != 'admin':
            return False, "Action non autorisée. Seuls les administrateurs peuvent supprimer des demandes de manière permanente."
            
        # Appeler la méthode de suppression permanente du modèle
        success, message = DemandeModel.permanently_delete_demande(demande_id)
        
        if success:
            # Logger l'activité
            ActivityLogModel.log_activity(
                admin_user_id, demande_id, 'admin_suppression_demande',
                f"Suppression définitive de la demande ID {demande_id} par l'admin"
            )
        
        return success, message
