"""
Modèle pour la gestion des participants aux demandes
"""
from typing import List, Dict, Any, Optional
from models.database import db

class ParticipantModel:
    """Modèle pour la gestion des participants"""
    
    @staticmethod
    def add_participant(demande_id: int, user_id: int, added_by_user_id: int) -> bool:
        """Ajouter un participant à une demande"""
        try:
            db.execute_query('''
                INSERT OR IGNORE INTO demande_participants 
                (demande_id, user_id, added_by_user_id)
                VALUES (?, ?, ?)
            ''', (demande_id, user_id, added_by_user_id))
            return True
        except Exception as e:
            print(f"Erreur ajout participant: {e}")
            return False
    
    @staticmethod
    def remove_participant(demande_id: int, user_id: int) -> bool:
        """Supprimer un participant d'une demande"""
        try:
            db.execute_query('''
                DELETE FROM demande_participants 
                WHERE demande_id = ? AND user_id = ?
            ''', (demande_id, user_id))
            return True
        except Exception as e:
            print(f"Erreur suppression participant: {e}")
            return False
    
    @staticmethod
    def get_participants(demande_id: int) -> List[Dict[str, Any]]:
        """Récupérer tous les participants d'une demande"""
        try:
            participants = db.execute_query('''
                SELECT dp.user_id, u.nom, u.prenom, u.email, u.role, u.region,
                       dp.added_by_user_id, dp.created_at
                FROM demande_participants dp
                JOIN users u ON dp.user_id = u.id
                WHERE dp.demande_id = ?
                ORDER BY dp.created_at
            ''', (demande_id,), fetch='all')
            
            return [dict(participant) for participant in participants] if participants else []
        except Exception as e:
            print(f"Erreur récupération participants: {e}")
            return []
    
    @staticmethod
    def is_participant(demande_id: int, user_id: int) -> bool:
        """Vérifier si un utilisateur est participant à une demande"""
        try:
            result = db.execute_query('''
                SELECT COUNT(*) FROM demande_participants 
                WHERE demande_id = ? AND user_id = ?
            ''', (demande_id, user_id), fetch='one')
            
            return result[0] > 0 if result else False
        except Exception as e:
            print(f"Erreur vérification participant: {e}")
            return False
    
    @staticmethod
    def add_multiple_participants(demande_id: int, user_ids: List[int], added_by_user_id: int) -> Dict[str, Any]:
        """Ajouter plusieurs participants à une demande"""
        results = {
            'success_count': 0,
            'failed_count': 0,
            'failed_users': []
        }
        
        for user_id in user_ids:
            if ParticipantModel.add_participant(demande_id, user_id, added_by_user_id):
                results['success_count'] += 1
            else:
                results['failed_count'] += 1
                results['failed_users'].append(user_id)
        
        return results
    
    @staticmethod
    def clear_participants(demande_id: int) -> bool:
        """Supprimer tous les participants d'une demande"""
        try:
            db.execute_query('''
                DELETE FROM demande_participants 
                WHERE demande_id = ?
            ''', (demande_id,))
            return True
        except Exception as e:
            print(f"Erreur suppression participants: {e}")
            return False
    
    @staticmethod
    def get_participant_summary(demande_id: int) -> Dict[str, Any]:
        """Récupérer un résumé des participants"""
        try:
            participants = ParticipantModel.get_participants(demande_id)
            
            summary = {
                'total_count': len(participants),
                'tc_count': len([p for p in participants if p['role'] == 'tc']),
                'dr_count': len([p for p in participants if p['role'] == 'dr']),
                'other_count': len([p for p in participants if p['role'] not in ['tc', 'dr']]),
                'participants': participants
            }
            
            return summary
        except Exception as e:
            print(f"Erreur résumé participants: {e}")
            return {
                'total_count': 0,
                'tc_count': 0,
                'dr_count': 0,
                'other_count': 0,
                'participants': []
            }
    
    @staticmethod
    def get_participants_for_display(demande_id: int, demandeur_participe: bool = True, 
                                   participants_libres: str = "") -> str:
        """Récupérer une chaîne formatée des participants pour affichage"""
        try:
            participants_db = ParticipantModel.get_participants(demande_id)
            
            # Construire la liste des participants
            participants_list = []
            
            # Ajouter les participants de la base de données
            for participant in participants_db:
                participants_list.append(f"{participant['prenom']} {participant['nom']} ({participant['role'].upper()})")
            
            # Ajouter les participants libres s'il y en a
            if participants_libres and participants_libres.strip():
                participants_list.append(participants_libres.strip())
            
            # Joindre tous les participants
            if participants_list:
                return " | ".join(participants_list)
            elif demandeur_participe:
                return "Demandeur uniquement"
            else:
                return "Aucun participant"
                
        except Exception as e:
            print(f"Erreur formatage participants: {e}")
            return "Erreur récupération participants"
