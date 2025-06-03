"""
Notification model and related operations
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd

from models.database import db

@dataclass
class Notification:
    """Notification data class"""
    id: Optional[int] = None
    user_id: int = 0
    demande_id: Optional[int] = None
    type_notification: str = ""
    titre: str = ""
    message: str = ""
    is_read: bool = False
    created_at: Optional[datetime] = None

class NotificationModel:
    """Notification model for database operations"""
    
    @staticmethod
    def add_notification(user_id: int, demande_id: Optional[int], 
                        type_notification: str, titre: str, message: str) -> bool:
        """Add a new notification"""
        try:
            db.execute_query('''
                INSERT INTO notifications (user_id, demande_id, type_notification, titre, message)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, demande_id, type_notification, titre, message))
            return True
        except Exception as e:
            print(f"Erreur ajout notification: {e}")
            return False
    
    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 10, 
                              unread_only: bool = False) -> pd.DataFrame:
        """Get notifications for a user"""
        try:
            where_clause = "WHERE n.user_id = ?"
            params = [user_id]
            
            if unread_only:
                where_clause += " AND n.is_read = FALSE"
            
            with db.get_connection() as conn:
                df = pd.read_sql_query(f'''
                    SELECT n.*, d.nom_manifestation
                    FROM notifications n
                    LEFT JOIN demandes d ON n.demande_id = d.id
                    {where_clause}
                    ORDER BY n.created_at DESC
                    LIMIT ?
                ''', conn, params=params + [limit])
                return df
        except Exception as e:
            print(f"Erreur récupération notifications: {e}")
            return pd.DataFrame()
    
    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark a notification as read"""
        try:
            db.execute_query('''
                UPDATE notifications 
                SET is_read = TRUE 
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))
            return True
        except Exception as e:
            print(f"Erreur marquage notification: {e}")
            return False
    
    @staticmethod
    def mark_all_as_read(user_id: int) -> bool:
        """Mark all notifications as read for a user"""
        try:
            db.execute_query('''
                UPDATE notifications 
                SET is_read = TRUE 
                WHERE user_id = ? AND is_read = FALSE
            ''', (user_id,))
            return True
        except Exception as e:
            print(f"Erreur marquage toutes notifications: {e}")
            return False
    
    @staticmethod
    def get_unread_count(user_id: int) -> int:
        """Get count of unread notifications"""
        try:
            result = db.execute_query('''
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND is_read = FALSE
            ''', (user_id,), fetch='one')
            return result[0] if result else 0
        except Exception as e:
            print(f"Erreur comptage notifications: {e}")
            return 0
    
    @staticmethod
    def delete_notification(notification_id: int, user_id: int) -> bool:
        """Delete a notification"""
        try:
            db.execute_query('''
                DELETE FROM notifications 
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))
            return True
        except Exception as e:
            print(f"Erreur suppression notification: {e}")
            return False
    
    @staticmethod
    def cleanup_old_notifications(days: int = 30) -> bool:
        """Cleanup old notifications (older than specified days)"""
        try:
            db.execute_query('''
                DELETE FROM notifications 
                WHERE created_at < datetime('now', '-' || ? || ' days')
            ''', (days,))
            return True
        except Exception as e:
            print(f"Erreur nettoyage notifications: {e}")
            return False
    
    @staticmethod
    def get_notification_stats() -> Dict[str, int]:
        """Get notification statistics"""
        try:
            total = db.execute_query(
                "SELECT COUNT(*) FROM notifications", fetch='one')[0]
            unread = db.execute_query(
                "SELECT COUNT(*) FROM notifications WHERE is_read = FALSE", fetch='one')[0]
            
            return {
                'total': total,
                'unread': unread,
                'read': total - unread
            }
        except Exception as e:
            print(f"Erreur stats notifications: {e}")
            return {'total': 0, 'unread': 0, 'read': 0}
