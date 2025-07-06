import requests
from datetime import datetime
from server.db.database import get_db
from server.sources.base_source import NewsSource


class TheNewsAPISource(NewsSource):
    def __init__(self, logger=None):
        super().__init__(logger)
        self.api_key = self._get_api_key_from_db()

    def _get_api_key_from_db(self):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT api_key FROM external_servers WHERE name = %s",
                ("The News API",),
            )
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else None
        except Exception as e:
            self.logger.error(f"Error fetching The News API key from DB: {e}")
            return None

    def fetch_articles(self):
        if not self.api_key:
            self.logger.error("THE_NEWS_API_KEY not configured.")
            return []

        url = f"https://api.thenewsapi.com/v1/news/top?language=en&api_token={self.api_key}"
        try:
            result = requests.get(url)
            if result.status_code != 200:
                self.logger.warning(f"TheNewsAPI failed: {result.status_code}")
                return []
            return self._parse_articles(result.json())
        except Exception as e:
            self.logger.error(f"Exception fetching articles from TheNewsAPI: {e}")
            return []

    def _parse_articles(self, data):
        articles = []
        try:
            conn = get_db()
            cursor = conn.cursor()
            for article in data.get("data", []):
                raw_category = article.get("category") or article.get("categories")
                category = (
                    raw_category
                    if isinstance(raw_category, str)
                    else (raw_category[0] if raw_category else "general")
                )
                cursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
                row = cursor.fetchone()
                category_id = row[0] if row else None
                articles.append(
                    {
                        "external_id": article.get("uuid"),
                        "title": article.get("title"),
                        "content": article.get("snippet") or "",
                        "url": article.get("url"),
                        "source": article.get("source"),
                        "category_id": category_id,
                        "published_at": self._parse_date(article.get("published_at")),
                    }
                )
            cursor.close()
        except Exception as e:
            self.logger.error(f"Error parsing articles from TheNewsAPI: {e}")
        return articles

    def get_source_name(self):
        return "The News API"

    def _parse_date(self, raw):
        try:
            return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except Exception:
            try:
                return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except Exception:
                self.logger.warning(f"Failed to parse date: {raw}")
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
