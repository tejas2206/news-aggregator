import logging
from server.db.database import get_db


class UserNotificationService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def get_notifications(self, email):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found", None, None
            cursor.execute(
                "SELECT category, enabled FROM notifications WHERE user_id = %s",
                (user["id"],),
            )
            categories = cursor.fetchall()
            cursor.execute(
                "SELECT keyword FROM user_keywords WHERE user_id = %s AND enabled = 1",
                (user["id"],),
            )
            keywords = [row["keyword"] for row in cursor.fetchall()]
            cursor.close()
            return True, None, categories, keywords
        except Exception as e:
            self.logger.error(f"Error fetching notifications: {e}")
            return False, "Failed to fetch notifications", None, None

    def toggle_category(self, email, category):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                """
                INSERT INTO notifications (user_id, category, enabled)
                VALUES (%s, %s, 1)
                ON DUPLICATE KEY UPDATE enabled = NOT enabled
            """,
                (user[0], category),
            )
            conn.commit()
            cursor.close()
            return True, f"Toggled notification for {category}."
        except Exception as e:
            self.logger.error(f"Error toggling category: {e}")
            return False, "Failed to toggle category."

    def add_keyword(self, email, keyword):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            
            cursor.execute(
                "SELECT id FROM user_keywords WHERE user_id = %s AND keyword = %s",
                (user[0], keyword),
            )
            existing_keyword = cursor.fetchone()
            if existing_keyword:
                cursor.close()
                return False, "Keyword already exists in your alerts."

            cursor.execute(
                """
                INSERT IGNORE INTO user_keywords (user_id, keyword, enabled)
                VALUES (%s, %s, 1)
            """,
                (user[0], keyword),
            )
            conn.commit()
            cursor.close()
            return True, "Keyword added to alerts."
        except Exception as e:
            self.logger.error(f"Error adding keyword: {e}")
            return False, "Failed to add keyword."

    def delete_keyword(self, email, keyword):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                "DELETE FROM user_keywords WHERE user_id = %s AND keyword = %s",
                (user[0], keyword),
            )

            if cursor.rowcount == 0:
                cursor.close()
                return False, "Keyword not found in your alerts."

            conn.commit()
            cursor.close()
            return True, "Keyword removed."
        except Exception as e:
            self.logger.error(f"Error deleting keyword: {e}")
            return False, "Failed to remove keyword."

    def get_notification_history(self, email):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found", None
            cursor.execute(
                """
                SELECT sn.message, sn.sent_at, na.title, na.url 
                FROM sent_notifications sn
                JOIN news_articles na ON sn.article_id = na.id
                WHERE sn.user_id = %s
                ORDER BY sn.sent_at DESC
            """,
                (user["id"],),
            )
            notifications = cursor.fetchall()
            cursor.close()
            return True, None, notifications
        except Exception as e:
            self.logger.error(f"Error fetching notification history: {e}")
            return False, "Failed to fetch notification history", None
