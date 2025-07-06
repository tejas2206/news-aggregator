import logging
from server.db.database import get_db


class UserFeedbackService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def like_article(self, email, article_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                """
                INSERT INTO article_feedback (user_id, article_id, feedback_type)
                VALUES (%s, %s, 'like')
                ON DUPLICATE KEY UPDATE feedback_type = 'like'
            """,
                (user[0], article_id),
            )
            conn.commit()
            cursor.close()
            return True, "You liked this article."
        except Exception as e:
            self.logger.error(f"Error liking article: {e}")
            return False, "Failed to like article."

    def dislike_article(self, email, article_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                """
                INSERT INTO article_feedback (user_id, article_id, feedback_type)
                VALUES (%s, %s, 'dislike')
                ON DUPLICATE KEY UPDATE feedback_type = 'dislike'
            """,
                (user[0], article_id),
            )
            conn.commit()
            cursor.close()
            return True, "You disliked this article."
        except Exception as e:
            self.logger.error(f"Error disliking article: {e}")
            return False, "Failed to dislike article."
