"""
User model and related operations
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

from models.database import db
from utils.security import hash_password, verify_password
from utils.validators import validate_email, validate_password

@dataclass
class User:
    """User data class"""
    id: Optional[int] = None
    email: str = ""
    nom: str = ""
    prenom: str = ""
    role: str = ""
    region: Optional[str] = None
    directeur_id: Optional[int] = None
    is_active: bool = False
    created_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None

class UserModel:
    """User model for database operations"""
    
    @staticmethod
    def create_user(email: str, nom: str, prenom: str, role: str, 
                   region: str = None, budget_alloue: float = 0, 
                   directeur_id: int = None, temp_password: str = None,
                   is_active: bool = False) -> tuple[bool, str | int]:
        """Create a new user"""
        try:
            if not validate_email(email):
                return False, "Format d'email invalide"
            
            password = temp_password or "TempPass123!"
            is_valid, message = validate_password(password)
            if not is_valid:
                return False, message
            
            # Vérifier email unique
            existing = db.execute_query(
                "SELECT id FROM users WHERE email = ?", 
                (email,), 
                fetch='one'
            )
            if existing:
                return False, "Cet email est déjà utilisé"
            
            hashed_password = hash_password(password)
            
            # Include is_active and activated_at if user is active on creation
            fields = 'email, password_hash, nom, prenom, role, region, directeur_id'
            values_tuple = (email, hashed_password, nom, prenom, role, region, directeur_id)

            if is_active:
                fields += ', is_active, activated_at'
                values_tuple += (True, 'CURRENT_TIMESTAMP')

            placeholders = ', '.join(['?' for _ in values_tuple])

            user_id = db.execute_query(f'''
                INSERT INTO users ({fields})
                VALUES ({placeholders})
            ''', values_tuple,
            fetch='lastrowid')
            
            return True, user_id
            
        except Exception as e:
            return False, f"Erreur: {e}"
    
    @staticmethod
    def authenticate(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user and return user info"""
        try:
            user_data = db.execute_query('''
                SELECT id, password_hash, nom, prenom, role, is_active, directeur_id, region
                FROM users WHERE email = ?
            ''', (email,), fetch='one')
            
            if user_data and verify_password(password, user_data['password_hash']):
                if user_data['is_active']:
                    return {
                        'id': user_data['id'],
                        'nom': user_data['nom'],
                        'prenom': user_data['prenom'],
                        'role': user_data['role'],
                        'directeur_id': user_data['directeur_id'],
                        'region': user_data['region'],
                        'email': email
                    }
                else:
                    return {'error': 'Compte non activé'}
            return None
            
        except Exception as e:
            print(f"Erreur authentification: {e}")
            return None
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """Activate a user account"""
        try:
            db.execute_query('''
                UPDATE users 
                SET is_active = TRUE, activated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            ''', (user_id,))
            return True
        except Exception as e:
            print(f"Erreur activation: {e}")
            return False
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user_data = db.execute_query('''
                SELECT id, email, nom, prenom, role, region, 
                       directeur_id, is_active, created_at, activated_at
                FROM users WHERE id = ?
            ''', (user_id,), fetch='one')
            
            return dict(user_data) if user_data else None
        except Exception as e:
            print(f"Erreur récupération utilisateur: {e}")
            return None
    
    @staticmethod
    def get_all_users() -> pd.DataFrame:
        """Get all users for admin panel"""
        try:
            with db.get_connection() as conn:
                df = pd.read_sql_query('''
                    SELECT u.id, u.email, u.nom, u.prenom, u.role, u.region, 
                           u.is_active, u.created_at, d.nom as directeur_nom, d.prenom as directeur_prenom
                    FROM users u
                    LEFT JOIN users d ON u.directeur_id = d.id
                    ORDER BY u.created_at DESC
                ''', conn)
                return df
        except Exception as e:
            print(f"Erreur récupération utilisateurs: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_directors() -> List[Dict[str, Any]]:
        """Get all active directors for TC assignment"""
        try:
            directors = db.execute_query('''
                SELECT id, nom, prenom, region 
                FROM users 
                WHERE role = 'dr' AND is_active = TRUE
                ORDER BY nom, prenom
            ''', fetch='all')
            
            return [dict(director) for director in directors] if directors else []
        except Exception as e:
            print(f"Erreur récupération directeurs: {e}")
            return []
    
    @staticmethod
    def get_team_members(director_id: int) -> List[Dict[str, Any]]:
        """Get team members for a director"""
        try:
            members = db.execute_query('''
                SELECT id, nom, prenom, email, role, region
                FROM users 
                WHERE directeur_id = ? AND is_active = TRUE
                ORDER BY nom, prenom
            ''', (director_id,), fetch='all')
            
            return [dict(member) for member in members] if members else []
        except Exception as e:
            print(f"Erreur récupération équipe: {e}")
            return []
    
    @staticmethod
    def update_user(user_id: int, **kwargs) -> bool:
        """Update user information"""
        try:
            if not kwargs:
                print(f"Avertissement: Aucune donnée à mettre à jour pour l'utilisateur {user_id}")
                return False
            
            # Afficher les données reçues pour debug
            print(f"Debug update_user: user_id={user_id}, kwargs={kwargs}")
            
            # Build dynamic update query
            set_clauses = []
            values = []
            
            # Liste des champs autorisés (incluant tous les champs modifiables)
            allowed_fields = [
                'nom', 'prenom', 'email', 'role', 'region', 
                'directeur_id', 'is_active'
            ]
            
            print(f"Debug: Champs autorisés: {allowed_fields}")

            for key, value in kwargs.items():
                if key in allowed_fields:
                    set_clauses.append(f"{key} = ?")
                    values.append(value)
                    print(f"Debug: Ajout du champ {key} = {value}")
                else:
                    print(f"Avertissement: Champ '{key}' non autorisé et ignoré")
            
            if not set_clauses:
                print("Erreur: Aucun champ valide à mettre à jour")
                return False
            
            values.append(user_id)
            query = f"UPDATE users SET {', '.join(set_clauses)} WHERE id = ?"
            
            print(f"Debug: Requête SQL: {query}")
            print(f"Debug: Valeurs: {values}")
            
            # Exécuter la requête
            result = db.execute_query(query, tuple(values))
            print(f"Debug: Résultat de la requête: {result}")
            
            # Vérifier que la mise à jour a bien eu lieu
            updated_user = db.execute_query(
                "SELECT * FROM users WHERE id = ?", 
                (user_id,), 
                fetch='one'
            )
            
            if updated_user:
                print(f"Debug: Utilisateur après mise à jour: {dict(updated_user)}")
                return True
            else:
                print(f"Erreur: Utilisateur {user_id} introuvable après mise à jour")
                return False
            
        except Exception as e:
            print(f"Erreur mise à jour utilisateur {user_id}: {e}")
            import traceback
            print(f"Traceback complet: {traceback.format_exc()}")
            return False
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """Delete a user (soft delete by deactivating)"""
        try:
            db.execute_query(
                "UPDATE users SET is_active = FALSE WHERE id = ?", 
                (user_id,)
            )
            return True
        except Exception as e:
            print(f"Erreur suppression utilisateur: {e}")
            return False
    
    @staticmethod
    def get_user_stats() -> Dict[str, Any]:
        """Get user statistics for admin dashboard"""
        try:
            with db.get_connection() as conn:
                stats = pd.read_sql_query('''
                    SELECT role, COUNT(*) as count, 
                           SUM(CASE WHEN is_active THEN 1 ELSE 0 END) as actifs
                    FROM users 
                    GROUP BY role
                ''', conn)
                
                return stats.to_dict('records') if not stats.empty else []
        except Exception as e:
            print(f"Erreur stats utilisateurs: {e}")
            return []
    
    @staticmethod
    def get_users_by_role(role: str, active_only: bool = False) -> List[Dict[str, Any]]:
        """Get users by role"""
        try:
            query = 'SELECT id, nom, prenom, email, region FROM users WHERE role = ?'
            params = [role]
            
            if active_only:
                query += ' AND is_active = TRUE'
            
            query += ' ORDER BY nom, prenom'
            
            users = db.execute_query(query, tuple(params), fetch='all')
            return [dict(user) for user in users] if users else []
        except Exception as e:
            print(f"Erreur récupération utilisateurs par rôle: {e}")
            return []
    
    @staticmethod
    def is_last_admin(user_id: int) -> bool:
        """Check if user is the last admin"""
        try:
            count = db.execute_query(
                "SELECT COUNT(*) FROM users WHERE role = 'admin' AND is_active = TRUE",
                fetch='one'
            )[0]
            
            user = db.execute_query(
                "SELECT role FROM users WHERE id = ?",
                (user_id,), fetch='one'
            )
            
            return count <= 1 and user and user['role'] == 'admin'
        except Exception as e:
            print(f"Erreur vérification dernier admin: {e}")
            return False
    
    @staticmethod
    def has_pending_requests(user_id: int) -> bool:
        """Check if user has pending requests"""
        try:
            count = db.execute_query(
                "SELECT COUNT(*) FROM demandes WHERE user_id = ? AND status NOT IN ('validee', 'rejetee')",
                (user_id,), fetch='one'
            )[0]
            
            return count > 0
        except Exception as e:
            print(f"Erreur vérification demandes en cours: {e}")
            return True  # Sécurité: on assume qu'il y en a
    
    @staticmethod
    def reset_password(user_id: int, new_password: str) -> bool:
        """Reset user password"""
        try:
            is_valid, message = validate_password(new_password)
            if not is_valid:
                return False
            
            hashed_password = hash_password(new_password)
            db.execute_query(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (hashed_password, user_id)
            )
            return True
        except Exception as e:
            print(f"Erreur réinitialisation mot de passe: {e}")
            return False
    
    @staticmethod
    def get_tc_users_by_region(region: str) -> List[Dict[str, Any]]:
        """Get all active TC users in a specific region"""
        try:
            tcs = db.execute_query('''
                SELECT id, nom, prenom, email, region
                FROM users 
                WHERE role = 'tc' AND is_active = TRUE AND region = ?
                ORDER BY nom, prenom
            ''', (region,), fetch='all')
            
            return [dict(tc) for tc in tcs] if tcs else []
        except Exception as e:
            print(f"Erreur récupération TCs par région: {e}")
            return []
    
    @staticmethod
    def get_tc_users_by_director(director_id: int) -> List[Dict[str, Any]]:
        """Get all TC users under a specific director"""
        try:
            tcs = db.execute_query('''
                SELECT id, nom, prenom, email, region
                FROM users 
                WHERE role = 'tc' AND is_active = TRUE AND directeur_id = ?
                ORDER BY nom, prenom
            ''', (director_id,), fetch='all')
            
            return [dict(tc) for tc in tcs] if tcs else []
        except Exception as e:
            print(f"Erreur récupération TCs par directeur: {e}")
            return []
    
    @staticmethod
    def permanently_delete_user(user_id: int) -> tuple[bool, str]:
        """Permanently delete a user and all related data (ADMIN ONLY)"""
        try:
            # Vérifier que ce n'est pas le dernier admin
            if UserModel.is_last_admin(user_id):
                return False, "Impossible de supprimer le dernier administrateur"
            
            # Récupérer les infos de l'utilisateur
            user_info = UserModel.get_user_by_id(user_id)
            if not user_info:
                return False, "Utilisateur introuvable"
            
            # Commencer une transaction
            with db.get_connection() as conn:
                conn.execute('BEGIN TRANSACTION')
                
                try:
                    # Ensure foreign key constraints are enabled in this connection
                    conn.execute('PRAGMA foreign_keys = ON')

                    # 1. Mettre à jour les demandes où cet utilisateur est valideur
                    # Mettre à NULL les références à l'utilisateur supprimé dans les demandes d'autres utilisateurs
                    conn.execute(
                         "UPDATE demandes SET valideur_dr_id = NULL WHERE valideur_dr_id = ?",
                         (user_id,)
                    )
                    conn.execute(
                         "UPDATE demandes SET valideur_financier_id = NULL WHERE valideur_financier_id = ?",
                         (user_id,)
                    )
                    conn.execute(
                         "UPDATE demandes SET valideur_dg_id = NULL WHERE valideur_dg_id = ?",
                         (user_id,)
                    )

                    # --- Cleanup dependents of demandes created by this user ---
                    # Get the IDs of demands created by this user
                    demande_ids_to_delete_result = conn.execute(
                        "SELECT id FROM demandes WHERE user_id = ?",
                        (user_id,)
                    ).fetchall()
                    demande_ids_to_delete = [row[0] for row in demande_ids_to_delete_result]
                    
                    if demande_ids_to_delete:
                         # Convert list of IDs to a string format suitable for SQL IN clause
                         demande_ids_str = ', '.join(map(str, demande_ids_to_delete))

                         # 2. Supprimer les logs d'activité liés aux demandes créées par cet utilisateur
                         conn.execute(
                              f"DELETE FROM activity_logs WHERE demande_id IN ({demande_ids_str})"
                         )

                         # 3. Supprimer les participants des demandes créées par cet utilisateur
                         conn.execute(
                             f"DELETE FROM demande_participants WHERE demande_id IN ({demande_ids_str})"
                         )

                         # 4. Supprimer les validations des demandes créées par cet utilisateur
                         conn.execute(
                              f"DELETE FROM demande_validations WHERE demande_id IN ({demande_ids_str})"
                         )

                         # 5. Supprimer les notifications liées aux demandes créées par cet utilisateur
                         conn.execute(
                              f"DELETE FROM notifications WHERE demande_id IN ({demande_ids_str})"
                         )

                         # Add deletion for a potential comments table
                         # Assuming a table named 'commentaires' with a foreign key 'demande_id'
                         try:
                              conn.execute(
                                   f"DELETE FROM commentaires WHERE demande_id IN ({demande_ids_str})"
                              )
                         except Exception as e:
                              # Log a warning but don't fail the transaction if the table doesn't exist
                              print(f"Warning: Could not delete from potential commentaires table: {e}")
                              pass # Continue the transaction even if this table doesn't exist

                         # Add deletion for a potential budget lines table
                         # Assuming a table named 'lignes_budgetaires' with a foreign key 'demande_id'
                         try:
                              conn.execute(
                                   f"DELETE FROM lignes_budgetaires WHERE demande_id IN ({demande_ids_str})"
                              )
                         except Exception as e:
                              print(f"Warning: Could not delete from potential lignes_budgetaires table: {e}")
                              pass # Continue

                         # Now, attempt to delete the demands themselves
                         conn.execute(
                             f"DELETE FROM demandes WHERE id IN ({demande_ids_str})"
                         )


                    # --- Cleanup other user-related dependents ---

                    # 6. Supprimer les participations de cet utilisateur à d'autres demandes (non créées par lui)
                    conn.execute(
                        "DELETE FROM demande_participants WHERE user_id = ?",
                        (user_id,)
                    )

                    # 7. Supprimer les validations effectuées par cet utilisateur dans n'importe quelle demande
                    conn.execute(
                        "DELETE FROM demande_validations WHERE validated_by = ?",
                        (user_id,)
                    )

                    # 8. Supprimer les notifications destinées spécifiquement à cet utilisateur
                    conn.execute(
                        "DELETE FROM notifications WHERE user_id = ?",
                        (user_id,)
                    )

                    # 9. Supprimer les logs d'activité liés à cet utilisateur (qui a effectué l'action ou qui est concerné)
                    conn.execute(
                        "DELETE FROM activity_logs WHERE user_id = ?",
                        (user_id,)
                    )
                    # Optionnel: Gérer les logs où l'utilisateur est la cible (target_user_id) si une telle colonne existe et a une FK

                    # 10. Mettre à jour les utilisateurs qui ont cet utilisateur comme directeur
                    subordinates_result = conn.execute(
                        "SELECT COUNT(*) FROM users WHERE directeur_id = ?",
                        (user_id,)
                    ).fetchone()
                    subordinates_count = subordinates_result[0] if subordinates_result else 0

                    if subordinates_count > 0:
                        # Mettre directeur_id à NULL pour les subordonnés
                        conn.execute(
                            "UPDATE users SET directeur_id = NULL WHERE directeur_id = ?",
                            (user_id,)
                        )

                    # 11. Supprimer l'utilisateur lui-même
                    conn.execute(
                        "DELETE FROM users WHERE id = ?",
                        (user_id,)
                    )

                    # Valider la transaction
                    conn.commit()

                    return True, f"Utilisateur {user_info['prenom']} {user_info['nom']} supprimé définitivement (avec {len(demande_ids_to_delete)} demande(s) créée(s) et {subordinates_count} subordonné(s) affecté(s))"

                except Exception as e:
                    conn.rollback()
                    # Re-raise the exception to be caught by the outer except block
                    raise e
                    
        except Exception as e:
            print(f"Erreur suppression définitive utilisateur {user_id}: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False, f"Erreur lors de la suppression: {str(e)}"
    
    @staticmethod
    def get_user_dependencies(user_id: int) -> Dict[str, int]:
        """Get the number of dependencies for a user before deletion"""
        try:
            dependencies = {
                'demandes_creees': 0,
                'participations': 0,
                'validations': 0,
                'notifications': 0,
                'subordonnes': 0
            }
            
            # Demandes créées
            result = db.execute_query(
                "SELECT COUNT(*) FROM demandes WHERE user_id = ?",
                (user_id,), fetch='one'
            )
            dependencies['demandes_creees'] = result[0] if result else 0
            
            # Participations
            result = db.execute_query(
                "SELECT COUNT(*) FROM demande_participants WHERE user_id = ?",
                (user_id,), fetch='one'
            )
            dependencies['participations'] = result[0] if result else 0
            
            # Validations
            result = db.execute_query(
                "SELECT COUNT(*) FROM demande_validations WHERE validated_by = ?",
                (user_id,), fetch='one'
            )
            dependencies['validations'] = result[0] if result else 0
            
            # Notifications
            result = db.execute_query(
                "SELECT COUNT(*) FROM notifications WHERE user_id = ?",
                (user_id,), fetch='one'
            )
            dependencies['notifications'] = result[0] if result else 0
            
            # Subordonnés
            result = db.execute_query(
                "SELECT COUNT(*) FROM users WHERE directeur_id = ?",
                (user_id,), fetch='one'
            )
            dependencies['subordonnes'] = result[0] if result else 0
            
            return dependencies
            
        except Exception as e:
            print(f"Erreur récupération dépendances utilisateur {user_id}: {e}")
            return {}
    
    @staticmethod
    def get_all_tc_users() -> List[Dict[str, Any]]:
        """Get all active TC users (for admin or cross-region access)"""
        try:
            tcs = db.execute_query('''
                SELECT id, nom, prenom, email, region
                FROM users 
                WHERE role = 'tc' AND is_active = TRUE
                ORDER BY region, nom, prenom
            ''', fetch='all')
            
            return [dict(tc) for tc in tcs] if tcs else []
        except Exception as e:
            print(f"Erreur récupération tous les TCs: {e}")
            return []

    @staticmethod
    def change_password(user_id: int, current_password: str, new_password: str) -> tuple[bool, str]:
        """Change the user's password in the database."""
        try:
            # 1. Get user by ID
            user_data = UserModel.get_user_by_id(user_id)
            if not user_data:
                return False, "Utilisateur non trouvé."

            # 2. Verify the current password
            if not verify_password(current_password, user_data['password_hash']):
                return False, "Mot de passe actuel incorrect."

            # 3. Hash the new password
            hashed_new_password = hash_password(new_password)

            # 4. Update the password in the database
            db.execute_query(
                '''
                UPDATE users
                SET password_hash = ?
                WHERE id = ?
                ''', (hashed_new_password, user_id)
            )

            return True, "Mot de passe mis à jour avec succès."

        except Exception as e:
            print(f"Erreur UserModel.change_password pour user_id {user_id}: {e}")
            return False, f"Une erreur est survenue lors de la mise à jour du mot de passe: {e}"

    @staticmethod
    def is_email_unique(email: str, exclude_user_id: Optional[int] = None) -> bool:
        """Check if an email is unique"""
        try:
            query = 'SELECT id FROM users WHERE email = ?'
            params = [email]
            
            if exclude_user_id:
                query += ' AND id != ?'
                params.append(exclude_user_id)
            
            existing = db.execute_query(query, tuple(params), fetch='one')
            return not existing
        except Exception as e:
            print(f"Erreur vérification email unique: {e}")
            return False

    @staticmethod
    def get_user_budgets(user_id: int) -> List[Dict[str, Any]]:
        """Get all fiscal year budgets for a user"""
        try:
            budgets = db.execute_query(
                '''
                SELECT id, fiscal_year, allocated_budget
                FROM user_budgets
                WHERE user_id = ?
                ORDER BY fiscal_year DESC
                ''',
                (user_id,), fetch='all'
            )
            return [dict(budget) for budget in budgets] if budgets else []
        except Exception as e:
            print(f"Erreur récupération budgets utilisateur {user_id}: {e}")
            return []

    @staticmethod
    def get_user_budget_for_year(user_id: int, fiscal_year: int) -> Optional[Dict[str, Any]]:
        """Get the allocated budget for a specific user and fiscal year"""
        try:
            budget = db.execute_query(
                '''
                SELECT id, fiscal_year, allocated_budget
                FROM user_budgets
                WHERE user_id = ? AND fiscal_year = ?
                ''',
                (user_id, fiscal_year), fetch='one'
            )
            return dict(budget) if budget else None
        except Exception as e:
            print(f"Erreur récupération budget {user_id} année {fiscal_year}: {e}")
            return None

    @staticmethod
    def add_user_budget(user_id: int, fiscal_year: int, allocated_budget: float) -> bool:
        """Add a new fiscal year budget for a user"""
        try:
            db.execute_query(
                '''
                INSERT INTO user_budgets (user_id, fiscal_year, allocated_budget)
                VALUES (?, ?, ?)
                ''',
                (user_id, fiscal_year, allocated_budget)
            )
            print(f"✅ Budget de {allocated_budget}€ ajouté pour l'utilisateur {user_id} en {fiscal_year}")
            return True
        except Exception as e:
            print(f"❌ Erreur ajout budget utilisateur {user_id} année {fiscal_year}: {e}")
            return False

    @staticmethod
    def update_user_budget(budget_id: int, allocated_budget: float) -> bool:
        """Update an existing fiscal year budget amount"""
        try:
            db.execute_query(
                '''
                UPDATE user_budgets
                SET allocated_budget = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (allocated_budget, budget_id)
            )
            print(f"✅ Budget ID {budget_id} mis à jour à {allocated_budget}€")
            return True
        except Exception as e:
            print(f"❌ Erreur mise à jour budget ID {budget_id}: {e}")
            return False

    @staticmethod
    def delete_user_budget(budget_id: int) -> bool:
        """Delete a fiscal year budget entry"""
        try:
            db.execute_query(
                '''
                DELETE FROM user_budgets
                WHERE id = ?
                ''',
                (budget_id,)
            )
            print(f"✅ Budget ID {budget_id} supprimé")
            return True
        except Exception as e:
            print(f"❌ Erreur suppression budget ID {budget_id}: {e}")
            return False

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Get a user by their email"""
        try:
            user_data = db.execute_query('''
                SELECT id, password_hash, nom, prenom, role, is_active, directeur_id, region
                FROM users WHERE email = ?
            ''', (email,), fetch='one')
            
            return dict(user_data) if user_data else None
        except Exception as e:
            print(f"Erreur récupération utilisateur par email: {e}")
            return None

    @staticmethod
    def get_user_budget_by_id(budget_id: int) -> Optional[Dict[str, Any]]:
        """Get a user budget entry by its ID"""
        try:
            budget_data = db.execute_query(
                '''
                SELECT id, user_id, fiscal_year, allocated_budget
                FROM user_budgets
                WHERE id = ?
                ''',
                (budget_id,), fetch='one'
            )
            return dict(budget_data) if budget_data else None
        except Exception as e:
            print(f"Erreur récupération budget par ID {budget_id}: {e}")
            return None
