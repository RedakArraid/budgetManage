"""
Controller for admin demande operations
"""
from typing import Optional, Tuple
from models.demande import DemandeModel

class AdminDemandeController:
    """Controller for admin demande operations"""
    
    @staticmethod
    def create_admin_demande(admin_id: int, selected_dr_id: Optional[int], 
                           type_demande: str, nom_manifestation: str, client: str, 
                           date_evenement: str, lieu: str, montant: float,
                           participants: str = "", commentaires: str = "", urgence: str = "normale",
                           budget: str = "", categorie: str = "", typologie_client: str = "",
                           groupe_groupement: str = "", region: str = "", agence: str = "",
                           client_enseigne: str = "", mail_contact: str = "", nom_contact: str = "",
                           demandeur_participe: bool = True, participants_libres: str = "",
                           auto_validate: bool = False, selected_participants: list = None,
                           by: str = "") -> Tuple[bool, Optional[int]]:
        """Create a demande as admin with DR selection and optional auto-validation"""
        try:
            # Créer la demande avec les spécificités admin
            success, demande_id = DemandeModel.create_demande_as_admin(
                admin_id=admin_id,
                selected_dr_id=selected_dr_id,
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
                participants_libres=participants_libres,
                auto_validate=auto_validate,
                by=by
            )
            
            # Ajouter les participants sélectionnés si la demande a été créée avec succès
            if success and demande_id and selected_participants:
                AdminDemandeController._add_selected_participants(demande_id, selected_participants, admin_id)
            
            return success, demande_id
            
        except Exception as e:
            print(f"Erreur contrôleur création demande admin: {e}")
            return False, None
    
    @staticmethod
    def _add_selected_participants(demande_id: int, selected_participants: list, added_by_admin_id: int):
        """Add selected participants to the demande"""
        try:
            from models.database import db
            
            for participant_id in selected_participants:
                # Éviter les doublons
                existing = db.execute_query('''
                    SELECT id FROM demande_participants 
                    WHERE demande_id = ? AND user_id = ?
                ''', (demande_id, participant_id), fetch='one')
                
                if not existing:
                    db.execute_query('''
                        INSERT INTO demande_participants (demande_id, user_id, added_by_user_id)
                        VALUES (?, ?, ?)
                    ''', (demande_id, participant_id, added_by_admin_id))
                    
        except Exception as e:
            print(f"Erreur ajout participants: {e}")
    
    @staticmethod
    def get_available_drs():
        """Get all available DRs for selection"""
        return DemandeModel.get_all_drs()
    
    @staticmethod
    def validate_admin_demande_data(nom_manifestation: str, client: str, lieu: str, 
                                   montant: float, date_evenement: str) -> Tuple[bool, list]:
        """Validate admin demande data"""
        errors = []
        
        # Validation des champs obligatoires
        if not nom_manifestation or len(nom_manifestation.strip()) < 3:
            errors.append("Le nom de la manifestation doit contenir au moins 3 caractères")
        
        if not client or len(client.strip()) < 2:
            errors.append("Le nom du client doit contenir au moins 2 caractères")
        
        if not lieu or len(lieu.strip()) < 2:
            errors.append("Le lieu doit contenir au moins 2 caractères")
        
        if montant <= 0:
            errors.append("Le montant doit être positif")
        
        if montant > 1000000:  # 1M€ maximum
            errors.append("Le montant semble trop élevé (maximum 1M€)")
        
        if not date_evenement:
            errors.append("La date d'événement est obligatoire")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_workflow_info(selected_dr_id: Optional[int], auto_validate: bool) -> str:
        """Get workflow information based on selection"""
        if auto_validate:
            return "🚀 **Validation directe** : La demande sera immédiatement validée et visible par tous les DRs/TCs concernés"
        elif selected_dr_id:
            return "📋 **Workflow normal** : La demande sera créée au nom du DR sélectionné et passera en validation financière"
        else:
            return "👤 **Création admin** : La demande sera créée en votre nom et suivra le workflow normal"
