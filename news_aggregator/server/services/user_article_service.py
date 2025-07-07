import logging
from server.db.database import get_db


class UserArticleService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def get_headlines_by_range(self, start, end, category="all"):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT keyword FROM blocked_keywords")
            keywords = [row["keyword"] for row in cursor.fetchall()]
            blocked_clauses = []
            blocked_params = []
            for keyword in keywords:
                blocked_clauses.append(
                    "(n.title NOT LIKE %s AND n.content NOT LIKE %s)"
                )
                blocked_params.extend([f"%{keyword}%", f"%{keyword}%"])
            query = """
                SELECT n.id, n.title, n.url, c.name as category
                FROM news_articles n
                LEFT JOIN categories c ON n.category_id = c.id
                WHERE DATE(n.created_at) BETWEEN %s AND %s
            """
            query_params = [start, end]
            if category != "all":
                query += " AND c.name = %s"
                query_params.append(category)
            query += " AND n.is_hidden = 0 AND (c.hidden = 0 OR c.hidden IS NULL)"
            if blocked_clauses:
                query += " AND " + " AND ".join(blocked_clauses)
                query_params.extend(blocked_params)
            query += " ORDER BY n.published_at DESC LIMIT 20"
            cursor.execute(query, query_params)
            rows = cursor.fetchall()
            cursor.close()
            return rows
        except Exception as e:
            self.logger.error(f"Error fetching headlines: {e}")
            return []

    def get_saved_articles(self, email):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                """
                SELECT sa.article_id, na.title, na.url, na.content, c.name as category
                FROM saved_articles sa
                JOIN users u ON sa.user_id = u.id
                JOIN news_articles na ON sa.article_id = na.id
                LEFT JOIN categories c ON na.category_id = c.id
                WHERE u.email = %s
                """,
                (email,),
            )
            articles = cursor.fetchall()
            cursor.close()
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching saved articles: {e}")
            return []

    def save_article(self, email, article_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                "INSERT INTO saved_articles (user_id, article_id) VALUES (%s, %s)",
                (user[0], article_id),
            )
            conn.commit()
            cursor.close()
            return True, f"Article {article_id} saved."
        except Exception as e:
            self.logger.error(f"Error saving article: {e}")
            return False, "Failed to save article."

    def delete_saved_article(self, email, article_id):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user:
                return False, "User not found"
            cursor.execute(
                "DELETE FROM saved_articles WHERE user_id = %s AND article_id = %s",
                (user[0], article_id),
            )
            conn.commit()
            cursor.close()
            return True, f"Article {article_id} deleted from saved list."
        except Exception as e:
            self.logger.error(f"Error deleting saved article: {e}")
            return False, "Failed to delete saved article."

    def search_articles(self, query, start_date, end_date, sort_by):
        try:
            sql = """
                SELECT
                    na.id,
                    na.title,
                    na.url,
                    na.content,
                    na.source,
                    na.published_at,
                    c.name AS category,
                    COALESCE(SUM(CASE WHEN af.feedback_type = 'like' THEN 1 ELSE 0 END), 0) AS likes,
                    COALESCE(SUM(CASE WHEN af.feedback_type = 'dislike' THEN 1 ELSE 0 END), 0) AS dislikes
                FROM news_articles na
                LEFT JOIN categories c ON na.category_id = c.id
                LEFT JOIN article_feedback af ON na.id = af.article_id
                WHERE (na.title LIKE %s OR na.content LIKE %s)
            """
            params = [f"%{query}%", f"%{query}%"]
            if start_date and end_date:
                sql += " AND DATE(na.published_at) BETWEEN %s AND %s"
                params.extend([start_date, end_date])
            sql += " GROUP BY na.id "
            if sort_by == "likes":
                sql += " ORDER BY likes DESC"
            elif sort_by == "dislikes":
                sql += " ORDER BY dislikes DESC"
            else:
                sql += " ORDER BY na.published_at DESC"
            sql += " LIMIT 10"
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params)
            articles = cursor.fetchall()
            cursor.close()
            return articles
        except Exception as e:
            self.logger.error(f"Error searching articles: {e}")
            return []

    def get_categories(self):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT name FROM categories WHERE hidden = 0 OR hidden IS NULL"
            )
            categories = [row["name"] for row in cursor.fetchall()]
            cursor.close()
            return categories
        except Exception as e:
            self.logger.error(f"Error fetching categories: {e}")
            return []
