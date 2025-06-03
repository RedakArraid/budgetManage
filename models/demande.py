"""
Demande model and related operations
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import pandas as pd

from models.database import db
from config.settings import WORKFLOW_CONFIG

def calculate_cy_by(date_evenement):
    """
    Calculer cy (année civile) et by (année fiscale) à partir de la date d'événement
    L'année fiscale commence en mai
    """
    if not date_evenement:
        return None, None
    
    # Convertir en datetime si c'est une string
    if isinstance(date_evenement, str):
        try:
            date_obj = datetime.strptime(date_evenement, '%Y-%m-%d').date()
        except ValueError:
            try:
                date_obj = datetime.strptime(date_evenement, '%d/%m/%Y').date()
            except ValueError:
                return None, None
    else:
        date_obj = date_evenement
    
    # cy = année civile (simple)
    cy = date_obj.year
    
    # by = année fiscale (commence en mai)
    if date_obj.month >= 5:  # Mai à décembre
        # Année fiscale actuelle : ex 2024/25
        by_start = cy
        by_end = cy + 1
    else:  # Janvier à avril
        # Année fiscale précédente : ex 23/24
        by_start = cy - 1
        by_end = cy
    
    # Format : YY/YY (ex: 23/24, 24/25)
    by = f"{str(by_start)[2:]}/{str(by_end)[2:]}"
    
    return cy, by

@dataclass
class Demande:
    """Demande data class"""
    id: Optional[int] = None
    
    budget: str = ""
    categorie: str = ""
    typologie_client: str = ""
    groupe_groupement: str = ""
    region: str = ""
    user_id: int = 0
    type_demande: str = ""
    nom_manifestation: str = ""
    client_enseigne: str = ""
    date_evenement: date = None
    lieu: str = ""
    agence: str = ""
    mail_contact: str = ""
    nom_contact: str = ""
    montant: float = 0.0
    commentaires: str = ""
    status: str = "brouillon"
    valideur_dr_id: Optional[int] = None
    valideur_financier_id: Optional[int] = None
    valideur_dg_id: Optional[int] = None
    date_validation_dr: Optional[datetime] = None
    date_validation_financier: Optional[datetime] = None
    date_validation_dg: Optional[datetime] = None
    commentaire_dr: str = ""
    commentaire_financier: str = ""
    commentaire_dg: str = ""
    cy: Optional[int] = None  # Année civile
    by: Optional[str] = None  # Année fiscale
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class DemandeModel:
    """Demande model for database operations"""
    
    @staticmethod
    def create_demande_as_admin(admin_id: int, selected_dr_id: Optional[int], 
                               type_demande: str, nom_manifestation: str, 
                               client: str, date_evenement: str, lieu: str, montant: float, 
                               participants: str = "", commentaires: str = "", urgence: str = "normale",
                               budget: str = "", categorie: str = "", typologie_client: str = "",
                               groupe_groupement: str = "", region: str = "", agence: str = "",
                               client_enseigne: str = "", mail_contact: str = "", nom_contact: str = "",
                               demandeur_participe: bool = True, participants_libres: str = "",
                               auto_validate: bool = False) -> tuple[bool, Optional[int]]:
        """Create a demande as admin with DR selection and optional auto-validation"""
        try:
            from utils.spinner_utils import OperationFeedback
            
            with OperationFeedback.create_demande():
                # Calculer cy et by à partir de la date d'événement
                cy, by = calculate_cy_by(date_evenement)
                
                # Si DR sélectionné, utiliser son ID comme user_id pour simuler qu'il a créé la demande
                # Sinon utiliser l'admin comme créateur
                creator_id = selected_dr_id if selected_dr_id else admin_id
                
                # Créer la demande
                demande_id = db.execute_query('''
                    INSERT INTO demandes (user_id, type_demande, nom_manifestation, client, date_evenement, 
                                        lieu, montant, participants, commentaires, urgence, budget, categorie, 
                                        typologie_client, groupe_groupement, region, agence, client_enseigne, 
                                        mail_contact, nom_contact, demandeur_participe, participants_libres, cy, by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (creator_id, type_demande, nom_manifestation, client, date_evenement, 
                      lieu, montant, participants, commentaires, urgence, budget, categorie, 
                      typologie_client, groupe_groupement, region, agence, client_enseigne, 
                      mail_contact, nom_contact, demandeur_participe, participants_libres, cy, by), 
                      fetch='lastrowid')
                
                # Si auto-validation demandée, valider directement avec l'admin comme valideur
                if auto_validate:
                    now = datetime.now().isoformat()
                    admin_info = db.execute_query('SELECT nom, prenom FROM users WHERE id = ?', (admin_id,), fetch='one')
                    admin_name = f"{admin_info['prenom']} {admin_info['nom']}" if admin_info else f"Admin #{admin_id}"
                    
                    comment = f"Validée directement par l'admin {admin_name}"
                    
                    # Valider à tous les niveaux avec l'admin comme valideur
                    DemandeModel.update_demande(
                        demande_id,
                        status='validee',
                        valideur_dr_id=admin_id,
                        valideur_financier_id=admin_id,
                        valideur_dg_id=admin_id,
                        date_validation_dr=now,
                        date_validation_financier=now,
                        date_validation_dg=now,
                        commentaire_dr=comment,
                        commentaire_financier=comment,
                        commentaire_dg=comment
                    )
                    
                    # Notifier les DRs et TCs concernés
                    DemandeModel._notify_admin_validation(demande_id, admin_id, selected_dr_id)
                else:
                    # Workflow normal : passer directement au status approprié selon le DR choisi
                    if selected_dr_id:
                        # La demande est créée au nom du DR, donc elle commence en attente financier
                        admin_info = db.execute_query('SELECT nom, prenom FROM users WHERE id = ?', (admin_id,), fetch='one')
                        admin_name = f"{admin_info['prenom']} {admin_info['nom']}" if admin_info else f"Admin #{admin_id}"
                        
                        DemandeModel.update_demande(
                            demande_id,
                            status='en_attente_financier',
                            valideur_dr_id=selected_dr_id,
                            date_validation_dr=datetime.now().isoformat(),
                            commentaire_dr=f"Créée et pré-validée par l'admin {admin_name}"
                        )
                
            return True, demande_id
        except Exception as e:
            print(f"Erreur création demande admin: {e}")
            return False, None
    
    @staticmethod
    def create_demande(user_id: int, type_demande: str, nom_manifestation: str, 
                      client: str, date_evenement: str, lieu: str, montant: float, 
                      participants: str = "", commentaires: str = "", urgence: str = "normale",
                      budget: str = "", categorie: str = "", typologie_client: str = "",
                      groupe_groupement: str = "", region: str = "", agence: str = "",
                      client_enseigne: str = "", mail_contact: str = "", nom_contact: str = "",
                      demandeur_participe: bool = True, participants_libres: str = "") -> tuple[bool, Optional[int]]:
        """Create a new demande with participant support (normal workflow)"""
        try:
            from utils.spinner_utils import OperationFeedback
            
            with OperationFeedback.create_demande():
                # Calculer cy et by à partir de la date d'événement
                cy, by = calculate_cy_by(date_evenement)
                
                demande_id = db.execute_query('''
                    INSERT INTO demandes (user_id, type_demande, nom_manifestation, client, date_evenement, 
                                        lieu, montant, participants, commentaires, urgence, budget, categorie, 
                                        typologie_client, groupe_groupement, region, agence, client_enseigne, 
                                        mail_contact, nom_contact, demandeur_participe, participants_libres, cy, by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, type_demande, nom_manifestation, client, date_evenement, 
                      lieu, montant, participants, commentaires, urgence, budget, categorie, 
                      typologie_client, groupe_groupement, region, agence, client_enseigne, 
                      mail_contact, nom_contact, demandeur_participe, participants_libres, cy, by), 
                      fetch='lastrowid')
            
            return True, demande_id
        except Exception as e:
            print(f"Erreur création demande: {e}")
            return False, None
    
    @staticmethod
    def _notify_admin_validation(demande_id: int, admin_id: int, selected_dr_id: Optional[int]):
        """Notify DRs and TCs when admin validates a demande directly"""
        try:
            # Récupérer les infos de la demande et de l'admin
            demande_info = db.execute_query('''
                SELECT nom_manifestation, client, montant, region
                FROM demandes WHERE id = ?
            ''', (demande_id,), fetch='one')
            
            admin_info = db.execute_query('''
                SELECT nom, prenom FROM users WHERE id = ?
            ''', (admin_id,), fetch='one')
            
            if not demande_info or not admin_info:
                return
            
            admin_name = f"{admin_info['prenom']} {admin_info['nom']}"
            
            # Notifier le DR sélectionné (s'il y en a un)
            if selected_dr_id:
                DemandeModel._create_notification(
                    user_id=selected_dr_id,
                    demande_id=demande_id,
                    type_notification='admin_validation',
                    titre='Demande validée par admin',
                    message=f"La demande '{demande_info['nom_manifestation']}' a été validée directement par l'admin {admin_name}. Montant: {demande_info['montant']:,.0f}€"
                )
            
            # Notifier tous les TCs de la région concernée
            if demande_info['region']:
                tcs_region = db.execute_query('''
                    SELECT id FROM users 
                    WHERE role = 'tc' AND region = ? AND is_active = TRUE
                ''', (demande_info['region'],), fetch='all')
                
                for tc in tcs_region or []:
                    DemandeModel._create_notification(
                        user_id=tc['id'],
                        demande_id=demande_id,
                        type_notification='admin_validation',
                        titre='Demande validée par admin',
                        message=f"Nouvelle demande validée par l'admin {admin_name}: '{demande_info['nom_manifestation']}' - {demande_info['client']} ({demande_info['montant']:,.0f}€)"
                    )
                    
        except Exception as e:
            print(f"Erreur notification admin validation: {e}")
    
    @staticmethod
    def _create_notification(user_id: int, demande_id: int, type_notification: str, titre: str, message: str):
        """Create a notification for a user"""
        try:
            db.execute_query('''
                INSERT INTO notifications (user_id, demande_id, type_notification, titre, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, demande_id, type_notification, titre, message))
        except Exception as e:
            print(f"Erreur création notification: {e}")
    
    @staticmethod
    def get_all_drs() -> List[Dict[str, Any]]:
        """Get all active DRs for admin demande creation"""
        try:
            drs = db.execute_query('''
                SELECT id, nom, prenom, email, region
                FROM users 
                WHERE role = 'dr' AND is_active = TRUE
                ORDER BY nom, prenom
            ''', fetch='all')
            
            return [dict(dr) for dr in drs] if drs else []
        except Exception as e:
            print(f"Erreur récupération DRs: {e}")
            return []
    
    @staticmethod
    def get_demandes_for_user(user_id: int, role: str, search_query: str = "", 
                             status_filter: str = "tous") -> pd.DataFrame:
        """Get demandes based on user role and filters, including demandes where user is participant"""
        try:
            with db.get_connection() as conn:
                # Build query based on role
                if role == 'admin':
                    base_query = '''
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                    '''
                    params = []
                elif role == 'tc':
                    # TC voit ses propres demandes ET les demandes où il est participant
                    base_query = '''
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        WHERE d.user_id = ?
                        UNION
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        JOIN demande_participants dp ON d.id = dp.demande_id
                        WHERE dp.user_id = ?
                    '''
                    params = [user_id, user_id]
                elif role == 'dr':
                    # DR voit ses propres demandes + celles de son équipe + celles où il est participant
                    base_query = '''
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        WHERE d.user_id = ? OR u.directeur_id = ?
                        UNION
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        JOIN demande_participants dp ON d.id = dp.demande_id
                        WHERE dp.user_id = ?
                    '''
                    params = [user_id, user_id, user_id]
                elif role in ['dr_financier', 'dg']:
                    base_query = '''
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        WHERE d.status IN ('en_attente_financier', 'validee')
                    '''
                    params = []
                elif role == 'marketing':
                    # Marketing voit ses propres demandes + celles où il est participant
                    base_query = '''
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        WHERE d.user_id = ?
                        UNION
                        SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                        FROM demandes d
                        JOIN users u ON d.user_id = u.id
                        JOIN demande_participants dp ON d.id = dp.demande_id
                        WHERE dp.user_id = ?
                    '''
                    params = [user_id, user_id]
                else:
                    return pd.DataFrame()
                
                # Add filters
                where_conditions = []
                if search_query:
                    where_conditions.append("(d.nom_manifestation LIKE ? OR d.client LIKE ? OR d.lieu LIKE ?)")
                    search_term = f"%{search_query}%"
                    params.extend([search_term, search_term, search_term])
                
                # Handle status_filter (string or list)
                if status_filter != "tous":
                    if isinstance(status_filter, list):
                        # Handle list of statuses
                        placeholders = ', '.join(['?' for _ in status_filter])
                        where_conditions.append(f"d.status IN ({placeholders})")
                        params.extend(status_filter)
                    else:
                        # Handle single status
                        where_conditions.append("d.status = ?")
                        params.append(status_filter)
                
                # Pour les requêtes UNION, nous devons encapsuler dans un SELECT externe pour les filtres
                if "UNION" in base_query and where_conditions:
                    base_query = f"SELECT * FROM ({base_query}) AS combined_results"
                    if where_conditions:
                        base_query += " WHERE " + " AND ".join(where_conditions)
                elif where_conditions:
                    if "WHERE" in base_query:
                        base_query += " AND " + " AND ".join(where_conditions)
                    else:
                        base_query += " WHERE " + " AND ".join(where_conditions)
                
                base_query += " ORDER BY updated_at DESC"
                
                df = pd.read_sql_query(base_query, conn, params=params)
                
                # Supprimer les doublons qui peuvent survenir avec les UNION
                if not df.empty and 'id' in df.columns:
                    df = df.drop_duplicates(subset=['id'])
                
                return df
        except Exception as e:
            print(f"Erreur récupération demandes: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_demande_by_id(demande_id: int) -> Optional[Dict[str, Any]]:
        """Get demande by ID with user info"""
        try:
            demande_data = db.execute_query('''
                SELECT d.*, u.nom, u.prenom, u.email, u.role as user_role
                FROM demandes d
                JOIN users u ON d.user_id = u.id
                WHERE d.id = ?
            ''', (demande_id,), fetch='one')
            
            return dict(demande_data) if demande_data else None
        except Exception as e:
            print(f"Erreur récupération demande: {e}")
            return None
    
    @staticmethod
    def update_demande(demande_id: int, **kwargs) -> bool:
        """Update demande information"""
        try:
            from utils.spinner_utils import OperationFeedback
            
            if not kwargs:
                return False
            
            with OperationFeedback.update_demande():
                # Build dynamic update query
                set_clauses = []
                values = []
                
                allowed_fields = [
                    'nom_manifestation', 'client', 'date_evenement', 'lieu', 'agence', 'montant', 'participants', 'commentaires', 'urgence',
                    'budget', 'categorie', 'typologie_client', 'groupe_groupement', 'region', 'client_enseigne', 'mail_contact', 'nom_contact',
                    'status', 'valideur_dr_id', 'valideur_financier_id', 'date_validation_dr',
                    'date_validation_financier', 'commentaire_dr', 'commentaire_financier',
                    'valideur_dg_id', 'date_validation_dg', 'commentaire_dg',
                    'demandeur_participe', 'participants_libres', 'cy', 'by'
                ]
                
                # Si la date d'événement change, recalculer cy et by
                if 'date_evenement' in kwargs:
                    cy, by = calculate_cy_by(kwargs['date_evenement'])
                    if cy and by:
                        kwargs['cy'] = cy
                        kwargs['by'] = by
                
                for key, value in kwargs.items():
                    if key in allowed_fields:
                        set_clauses.append(f"{key} = ?")
                        values.append(value)
                
                if not set_clauses:
                    return False
                
                # Always update updated_at
                set_clauses.append("updated_at = CURRENT_TIMESTAMP")
                values.append(demande_id)
                
                query = f"UPDATE demandes SET {', '.join(set_clauses)} WHERE id = ?"
                
                db.execute_query(query, tuple(values))
                return True
            
        except Exception as e:
            print(f"Erreur mise à jour demande: {e}")
            return False
    
    @staticmethod
    def submit_demande(demande_id: int, user_id: int) -> tuple[bool, str]:
        """Submit a demande for approval"""
        try:
            # Get demande and user info
            demande_data = db.execute_query('''
                SELECT d.nom_manifestation, d.type_demande, d.user_id, u.role, u.directeur_id, u.nom, u.prenom
                FROM demandes d
                JOIN users u ON d.user_id = u.id
                WHERE d.id = ? AND d.user_id = ?
            ''', (demande_id, user_id), fetch='one')
            
            if not demande_data:
                return False, "Demande non trouvée"
            
            type_demande = demande_data['type_demande']
            user_role = demande_data['role']
            directeur_id = demande_data['directeur_id']
            
            # Determine next status and validation updates based on workflow
            update_data = {}
            
            if type_demande == 'budget':
                if user_role == 'tc' and directeur_id:
                    # TC soumet vers son DR
                    update_data['status'] = 'en_attente_dr'
                elif user_role == 'dr':
                    # DR soumet sa propre demande OU valide une demande de son équipe
                    # Dans les deux cas, on marque la validation DR comme faite
                    update_data.update({
                        'status': 'en_attente_financier',
                        'valideur_dr_id': user_id,
                        'date_validation_dr': datetime.now().isoformat(),
                        'commentaire_dr': f'Validé automatiquement lors de la soumission par {demande_data["prenom"]} {demande_data["nom"]}'
                    })
                else:
                    return False, "Workflow non défini pour ce rôle"
            elif type_demande == 'marketing':
                # Marketing va directement au financier
                update_data['status'] = 'en_attente_financier'
            else:
                return False, "Type de demande non valide"
            
            # Update demande with the determined data
            DemandeModel.update_demande(demande_id, **update_data)
            
            return True, "Demande soumise avec succès"
            
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def validate_demande(demande_id: int, valideur_id: int, action: str, 
                        commentaire: str = "") -> tuple[bool, str]:
        """Validate or reject a demande - Utilise le moteur centralisé"""
        try:
            from services.validation_engine import validation_engine
            return validation_engine.validate_demande(demande_id, valideur_id, action, commentaire)
        except Exception as e:
            print(f"Erreur validation demande: {e}")
            return False, f"Erreur: {e}"
    
    @staticmethod
    def get_dashboard_stats(user_id: int, role: str) -> Dict[str, Any]:
        """Get statistics for dashboard based on user role"""
        try:
            stats = {}
            
            if role == 'admin':
                # Global stats for admin
                stats['total_demandes'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes", fetch='one')[0]
                stats['en_attente_dr'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE status = 'en_attente_dr'", fetch='one')[0]
                stats['en_attente_financier'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE status = 'en_attente_financier'", fetch='one')[0]
                stats['validees'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE status = 'validee'", fetch='one')[0]
                
                result = db.execute_query(
                    "SELECT SUM(montant) FROM demandes WHERE status = 'validee'", fetch='one')[0]
                stats['montant_valide'] = result if result else 0
                
            elif role == 'tc':
                # Stats for TC
                stats['mes_demandes'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE user_id = ?", (user_id,), fetch='one')[0]
                stats['validees'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE user_id = ? AND status = 'validee'", 
                    (user_id,), fetch='one')[0]
                
                result = db.execute_query(
                    "SELECT SUM(montant) FROM demandes WHERE user_id = ? AND status = 'validee'", 
                    (user_id,), fetch='one')[0]
                stats['montant_valide'] = result if result else 0
                
            elif role == 'dr':
                # Stats for DR
                stats['total_demandes'] = db.execute_query('''
                    SELECT COUNT(*) FROM demandes d
                    JOIN users u ON d.user_id = u.id
                    WHERE d.user_id = ? OR u.directeur_id = ?
                ''', (user_id, user_id), fetch='one')[0]
                
                stats['en_attente_validation'] = db.execute_query('''
                    SELECT COUNT(*) FROM demandes d
                    JOIN users u ON d.user_id = u.id
                    WHERE (d.user_id = ? OR u.directeur_id = ?) AND d.status = 'en_attente_dr'
                ''', (user_id, user_id), fetch='one')[0]
                
            elif role in ['dr_financier', 'dg']:
                # Stats for financiers
                stats['en_attente_validation'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE status = 'en_attente_financier'", fetch='one')[0]
                stats['validees'] = db.execute_query(
                    "SELECT COUNT(*) FROM demandes WHERE status = 'validee'", fetch='one')[0]
                
                result = db.execute_query(
                    "SELECT SUM(montant) FROM demandes WHERE status = 'validee'", fetch='one')[0]
                stats['montant_valide'] = result if result else 0
            
            return stats
        except Exception as e:
            print(f"Erreur stats: {e}")
            return {}
    
    @staticmethod
    def get_analytics_data(user_id: int, role: str) -> Dict[str, Any]:
        """Get analytics data for charts and reports"""
        try:
            # Get demandes dataframe
            demandes_df = DemandeModel.get_demandes_for_user(user_id, role)
            
            if demandes_df.empty:
                return {}
            
            # Convert date column
            demandes_df['date_evenement'] = pd.to_datetime(demandes_df['date_evenement'])
            demandes_df['mois'] = demandes_df['date_evenement'].dt.to_period('M')
            
            # Monthly evolution
            monthly_data = demandes_df.groupby('mois')['montant'].agg(['sum', 'count']).reset_index()
            monthly_data['mois'] = monthly_data['mois'].astype(str)
            
            # Status distribution
            status_data = demandes_df.groupby('status').size().reset_index(name='count')
            
            # Top clients
            client_data = demandes_df.groupby('client').agg({
                'montant': ['sum', 'count']
            }).reset_index()
            client_data.columns = ['client', 'montant_total', 'nb_demandes']
            client_data = client_data.sort_values('montant_total', ascending=False).head(10)
            
            return {
                'monthly_evolution': monthly_data.to_dict('records'),
                'status_distribution': status_data.to_dict('records'),
                'top_clients': client_data.to_dict('records'),
                'summary': {
                    'total_demandes': len(demandes_df),
                    'montant_total': demandes_df['montant'].sum(),
                    'montant_moyen': demandes_df['montant'].mean(),
                    'taux_validation': (len(demandes_df[demandes_df['status'] == 'validee']) / len(demandes_df) * 100) if len(demandes_df) > 0 else 0
                }
            }
            
        except Exception as e:
            print(f"Erreur analytics: {e}")
            return {}
    
    @staticmethod
    def permanently_delete_demande(demande_id: int) -> tuple[bool, str]:
        """Permanently delete a demande and all related data (ADMIN ONLY)"""
        try:
            # Récupérer les infos de la demande
            demande_info = db.execute_query('''
                SELECT d.nom_manifestation, d.client, d.montant, d.status, 
                       u.nom as creator_nom, u.prenom as creator_prenom
                FROM demandes d
                JOIN users u ON d.user_id = u.id
                WHERE d.id = ?
            ''', (demande_id,), fetch='one')
            
            if not demande_info:
                return False, "Demande introuvable"
            
            # Commencer une transaction
            with db.get_connection() as conn:
                conn.execute('BEGIN TRANSACTION')
                
                try:
                    # 1. Supprimer les participants
                    participants_result = conn.execute(
                        "SELECT COUNT(*) FROM demande_participants WHERE demande_id = ?",
                        (demande_id,)
                    ).fetchone()
                    participants_count = participants_result[0] if participants_result else 0
                    
                    if participants_count > 0:
                        conn.execute(
                            "DELETE FROM demande_participants WHERE demande_id = ?",
                            (demande_id,)
                        )
                    
                    # 2. Supprimer les validations
                    validations_result = conn.execute(
                        "SELECT COUNT(*) FROM demande_validations WHERE demande_id = ?",
                        (demande_id,)
                    ).fetchone()
                    validations_count = validations_result[0] if validations_result else 0
                    
                    if validations_count > 0:
                        conn.execute(
                            "DELETE FROM demande_validations WHERE demande_id = ?",
                            (demande_id,)
                        )
                    
                    # 3. Supprimer les notifications liées
                    notifications_result = conn.execute(
                        "SELECT COUNT(*) FROM notifications WHERE demande_id = ?",
                        (demande_id,)
                    ).fetchone()
                    notifications_count = notifications_result[0] if notifications_result else 0
                    
                    if notifications_count > 0:
                        conn.execute(
                            "DELETE FROM notifications WHERE demande_id = ?",
                            (demande_id,)
                        )
                    
                    # 4. Supprimer les logs d'activité liés
                    activity_logs_count = 0
                    try:
                        activity_logs_result = conn.execute(
                            "SELECT COUNT(*) FROM activity_logs WHERE demande_id = ?",
                            (demande_id,)
                        ).fetchone()
                        activity_logs_count = activity_logs_result[0] if activity_logs_result else 0
                        
                        if activity_logs_count > 0:
                            conn.execute(
                                "DELETE FROM activity_logs WHERE demande_id = ?",
                                (demande_id,)
                            )
                    except Exception:
                        # La table activity_logs peut ne pas avoir de colonne demande_id
                        pass
                    
                    # 5. Supprimer la demande elle-même
                    conn.execute(
                        "DELETE FROM demandes WHERE id = ?",
                        (demande_id,)
                    )
                    
                    # Valider la transaction
                    conn.commit()
                    
                    creator_name = f"{demande_info['creator_prenom']} {demande_info['creator_nom']}"
                    summary = f"Demande '{demande_info['nom_manifestation']}' de {creator_name} supprimée définitivement"
                    details = f"({participants_count} participant(s), {validations_count} validation(s), {notifications_count} notification(s) supprimé(s))"
                    
                    return True, f"{summary} {details}"
                    
                except Exception as e:
                    conn.rollback()
                    raise e
                    
        except Exception as e:
            print(f"Erreur suppression définitive demande {demande_id}: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    @staticmethod
    def get_demande_dependencies(demande_id: int) -> Dict[str, int]:
        """Get the number of dependencies for a demande before deletion"""
        try:
            dependencies = {
                'participants': 0,
                'validations': 0,
                'notifications': 0,
                'activity_logs': 0
            }
            
            # Participants
            result = db.execute_query(
                "SELECT COUNT(*) FROM demande_participants WHERE demande_id = ?",
                (demande_id,), fetch='one'
            )
            dependencies['participants'] = result[0] if result else 0
            
            # Validations
            result = db.execute_query(
                "SELECT COUNT(*) FROM demande_validations WHERE demande_id = ?",
                (demande_id,), fetch='one'
            )
            dependencies['validations'] = result[0] if result else 0
            
            # Notifications
            result = db.execute_query(
                "SELECT COUNT(*) FROM notifications WHERE demande_id = ?",
                (demande_id,), fetch='one'
            )
            dependencies['notifications'] = result[0] if result else 0
            
            # Activity logs (optionnel car la colonne peut ne pas exister)
            try:
                result = db.execute_query(
                    "SELECT COUNT(*) FROM activity_logs WHERE demande_id = ?",
                    (demande_id,), fetch='one'
                )
                dependencies['activity_logs'] = result[0] if result else 0
            except Exception:
                dependencies['activity_logs'] = 0
            
            return dependencies
            
        except Exception as e:
            print(f"Erreur récupération dépendances demande {demande_id}: {e}")
            return {}
