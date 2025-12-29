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

            user_id = user[0]

            cursor.execute(
                "SELECT feedback_type FROM article_feedback WHERE user_id = %s AND article_id = %s",
                (user_id, article_id),
            )
            existing_feedback = cursor.fetchone()

            if existing_feedback:
                if existing_feedback[0] == "like":
                    return False, "You have already liked this article."
                else:
                    cursor.execute(
                        "UPDATE article_feedback SET feedback_type = 'like' WHERE user_id = %s AND article_id = %s",
                        (user_id, article_id),
                    )
            else:
                cursor.execute(
                    "INSERT INTO article_feedback (user_id, article_id, feedback_type) VALUES (%s, %s, 'like')",
                    (user_id, article_id),
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

            user_id = user[0]

            cursor.execute(
                "SELECT feedback_type FROM article_feedback WHERE user_id = %s AND article_id = %s",
                (user_id, article_id),
            )
            existing_feedback = cursor.fetchone()

            if existing_feedback:
                if existing_feedback[0] == "dislike":
                    return False, "You have already disliked this article."
                else:
                    cursor.execute(
                        "UPDATE article_feedback SET feedback_type = 'dislike' WHERE user_id = %s AND article_id = %s",
                        (user_id, article_id),
                    )
            else:
                cursor.execute(
                    "INSERT INTO article_feedback (user_id, article_id, feedback_type) VALUES (%s, %s, 'dislike')",
                    (user_id, article_id),
                )

            conn.commit()
            cursor.close()
            return True, "You disliked this article."
        except Exception as e:
            self.logger.error(f"Error disliking article: {e}")
            return False, "Failed to dislike article."
