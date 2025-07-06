import logging
from server.db.database import get_db
from server.services.notification_service import NotificationService


class ArticleReportService:
    def __init__(self, notification_service=None, logger=None):
        self.logger = logger or logging.getLogger(__name__)
        self.notification_service = notification_service or NotificationService()

    def report_article(self, email, article_id, report_threshold=2):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            user_id = user[0]
            try:
                cursor.execute(
                    "INSERT INTO article_reports (user_id, article_id) VALUES (%s, %s)",
                    (user_id, article_id),
                )
                conn.commit()
            except Exception:
                return False, "You have already reported this article."
            cursor.execute(
                "SELECT COUNT(*) FROM article_reports WHERE article_id = %s",
                (article_id,),
            )
            report_count = cursor.fetchone()[0]
            if report_count >= report_threshold:
                cursor.execute(
                    "UPDATE news_articles SET is_hidden = 1 WHERE id = %s",
                    (article_id,),
                )
                conn.commit()
            self.notification_service.notify_admin_about_report(article_id, email)
            cursor.close()
            return True, "Article reported successfully."
        except Exception as e:
            self.logger.error(f"Error reporting article: {e}")
            return False, "Failed to report article."
