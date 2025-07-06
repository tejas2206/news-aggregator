import logging
from server.db.database import get_db


class AdminService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def get_server_status(self):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT id, name, status, last_accessed FROM external_servers"
            )
            servers = cursor.fetchall()
            cursor.close()
            return servers
        except Exception as e:
            self.logger.error(f"Error fetching server status: {e}")
            return []

    def get_server_details(self):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT id, name, api_key FROM external_servers")
            servers = cursor.fetchall()
            cursor.close()
            return servers
        except Exception as e:
            self.logger.error(f"Error fetching server details: {e}")
            return []

    def update_server_api_key(self, server_id, new_key):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE external_servers SET api_key = %s WHERE id = %s",
                (new_key, server_id),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error updating API key: {e}")
            return False

    def add_category(self, name):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("INSERT IGNORE INTO categories (name) VALUES (%s)", (name,))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error adding category: {e}")
            return False

    def get_reported_articles(self):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT 
                    MAX(na.id) AS id,
                    MAX(na.title) AS title,
                    MAX(na.url) AS url,
                    MAX(na.content) AS content,
                    COUNT(ar.id) AS report_count
                FROM article_reports ar
                JOIN news_articles na ON ar.article_id = na.id
                WHERE na.is_hidden = 1 or na.is_hidden = 0
                GROUP BY ar.article_id
                ORDER BY report_count DESC
            """
            )
            reports = cursor.fetchall()
            cursor.close()
            return reports
        except Exception as e:
            self.logger.error(f"Error fetching reported articles: {e}")
            return []

    def hide_article(self, article_id, hide=True):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE news_articles SET is_hidden = %s WHERE id = %s",
                (hide, article_id),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error hiding article: {e}")
            return False

    def toggle_category_visibility(self, category_name):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE categories
                SET hidden = NOT hidden
                WHERE name = %s
            """,
                (category_name,),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error toggling category visibility: {e}")
            return False

    def add_blocked_keyword(self, keyword):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT IGNORE INTO blocked_keywords (keyword)
                VALUES (%s)
            """,
                (keyword,),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error adding blocked keyword: {e}")
            return False

    def remove_blocked_keyword(self, keyword):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                """
                DELETE FROM blocked_keywords
                WHERE keyword = %s
            """,
                (keyword,),
            )
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            self.logger.error(f"Error removing blocked keyword: {e}")
            return False

    def get_blocked_keywords(self):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT keyword FROM blocked_keywords")
            keywords = [row["keyword"] for row in cursor.fetchall()]
            cursor.close()
            return keywords
        except Exception as e:
            self.logger.error(f"Error fetching blocked keywords: {e}")
            return []
