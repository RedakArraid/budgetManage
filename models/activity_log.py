"""
Activity log model and related operations
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

from models.database import db

@dataclass
class ActivityLog:
    """Activity log data class"""
    id: Optional[int] = None
    user_id: int = 0
    demande_id: Optional[int] = None
    action: str = ""
    details: str = ""
    created_at: Optional[datetime] = None

class ActivityLogModel:
    """Activity log model for database operations"""
    
    @staticmethod
    def log_activity(user_id: int, demande_id: Optional[int], 
                    action: str, details: str = "") -> bool:
        """Log an activity"""
        try:
            db.execute_query('''
                INSERT INTO activity_logs (user_id, demande_id, action, details)
                VALUES (?, ?, ?, ?)
            ''', (user_id, demande_id, action, details))
            return True
        except Exception as e:
            print(f"Erreur log activité: {e}")
            return False
    
    @staticmethod
    def get_activity_logs(user_id: Optional[int] = None, demande_id: Optional[int] = None,
                         limit: int = 50) -> pd.DataFrame:
        """Get activity logs with optional filters"""
        try:
            where_conditions = []
            params = []
            
            if user_id:
                where_conditions.append("a.user_id = ?")
                params.append(user_id)
            
            if demande_id:
                where_conditions.append("a.demande_id = ?")
                params.append(demande_id)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            with db.get_connection() as conn:
                df = pd.read_sql_query(f'''
                    SELECT a.*, u.nom, u.prenom, u.role, d.nom_manifestation
                    FROM activity_logs a
                    JOIN users u ON a.user_id = u.id
                    LEFT JOIN demandes d ON a.demande_id = d.id
                    {where_clause}
                    ORDER BY a.created_at DESC
                    LIMIT ?
                ''', conn, params=params + [limit])
                return df
        except Exception as e:
            print(f"Erreur récupération logs: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_demande_history(demande_id: int) -> pd.DataFrame:
        """Get complete history for a specific demande"""
        try:
            with db.get_connection() as conn:
                df = pd.read_sql_query('''
                    SELECT a.*, u.nom, u.prenom, u.role
                    FROM activity_logs a
                    JOIN users u ON a.user_id = u.id
                    WHERE a.demande_id = ?
                    ORDER BY a.created_at ASC
                ''', conn, params=[demande_id])
                return df
        except Exception as e:
            print(f"Erreur historique demande: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_user_activity(user_id: int, limit: int = 20) -> pd.DataFrame:
        """Get recent activity for a user"""
        try:
            with db.get_connection() as conn:
                df = pd.read_sql_query('''
                    SELECT a.*, d.nom_manifestation, d.client
                    FROM activity_logs a
                    LEFT JOIN demandes d ON a.demande_id = d.id
                    WHERE a.user_id = ?
                    ORDER BY a.created_at DESC
                    LIMIT ?
                ''', conn, params=[user_id, limit])
                return df
        except Exception as e:
            print(f"Erreur activité utilisateur: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def get_activity_stats(days: int = 30) -> Dict[str, Any]:
        """Get activity statistics for the last X days"""
        try:
            with db.get_connection() as conn:
                # Activity by action type
                action_stats = pd.read_sql_query('''
                    SELECT action, COUNT(*) as count
                    FROM activity_logs
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY action
                    ORDER BY count DESC
                ''', conn, params=[days])
                
                # Activity by day
                daily_stats = pd.read_sql_query('''
                    SELECT DATE(created_at) as date, COUNT(*) as count
                    FROM activity_logs
                    WHERE created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY DATE(created_at)
                    ORDER BY date DESC
                ''', conn, params=[days])
                
                # Most active users
                user_stats = pd.read_sql_query('''
                    SELECT u.nom, u.prenom, u.role, COUNT(a.id) as activity_count
                    FROM activity_logs a
                    JOIN users u ON a.user_id = u.id
                    WHERE a.created_at >= datetime('now', '-' || ? || ' days')
                    GROUP BY a.user_id, u.nom, u.prenom, u.role
                    ORDER BY activity_count DESC
                    LIMIT 10
                ''', conn, params=[days])
                
                return {
                    'action_stats': action_stats.to_dict('records'),
                    'daily_stats': daily_stats.to_dict('records'),
                    'user_stats': user_stats.to_dict('records')
                }
        except Exception as e:
            print(f"Erreur stats activité: {e}")
            return {}
    
    @staticmethod
    def cleanup_old_logs(days: int = 90) -> bool:
        """Cleanup old activity logs (older than specified days)"""
        try:
            db.execute_query('''
                DELETE FROM activity_logs 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            return True
        except Exception as e:
            print(f"Erreur nettoyage logs: {e}")
            return False
    
    @staticmethod
    def export_logs(start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """Export activity logs for a date range"""
        try:
            where_conditions = []
            params = []
            
            if start_date:
                where_conditions.append("DATE(a.created_at) >= ?")
                params.append(start_date)
            
            if end_date:
                where_conditions.append("DATE(a.created_at) <= ?")
                params.append(end_date)
            
            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)
            
            with db.get_connection() as conn:
                df = pd.read_sql_query(f'''
                    SELECT a.created_at, u.nom, u.prenom, u.role, u.email,
                           a.action, a.details, d.nom_manifestation, d.client
                    FROM activity_logs a
                    JOIN users u ON a.user_id = u.id
                    LEFT JOIN demandes d ON a.demande_id = d.id
                    {where_clause}
                    ORDER BY a.created_at DESC
                ''', conn, params=params)
                return df
        except Exception as e:
            print(f"Erreur export logs: {e}")
            return pd.DataFrame()
