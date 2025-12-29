import requests
from datetime import datetime
from server.db.database import get_db
from server.sources.base_source import NewsSource


class NewsAPISource(NewsSource):
    def __init__(self, logger=None):
        super().__init__(logger)
        self.api_key = self._get_api_key_from_db()
        self.categories = [
            "business",
            "entertainment",
            "general",
            "health",
            "science",
            "sports",
            "technology",
        ]

    def _get_api_key_from_db(self):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT api_key FROM external_servers WHERE name = %s", ("News API",)
            )
            row = cursor.fetchone()
            cursor.close()
            return row[0] if row else None
        except Exception as e:
            self.logger.error(f"Error fetching News API key from DB: {e}")
            return None

    def fetch_articles(self):
        if not self.api_key:
            self.logger.error("NEWS_API_KEY not configured.")
            return []

        all_articles = []
        for category in self.categories:
            url = (
                f"https://newsapi.org/v2/top-headlines"
                f"?country=us&category={category}&pageSize=10&apiKey={self.api_key}"
            )
            try:
                result = requests.get(url)
                if result.status_code != 200:
                    self.logger.warning(
                        f"NewsAPI failed for category '{category}': {result.status_code}"
                    )
                    continue
                all_articles.extend(self._parse_articles(result.json(), category))
            except Exception as e:
                self.logger.error(f"Exception fetching articles for {category}: {e}")
        return all_articles

    def _parse_articles(self, data, category):
        articles = []
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM categories WHERE name = %s", (category.lower(),)
            )
            row = cursor.fetchone()
            category_id = row[0] if row else None

            for article in data.get("articles", []):
                articles.append(
                    {
                        "external_id": article.get("url"),
                        "title": article.get("title"),
                        "content": article.get("description") or "",
                        "url": article.get("url"),
                        "source": article.get("source", {}).get("name"),
                        "category_id": category_id,
                        "published_at": self._parse_date(article.get("publishedAt")),
                    }
                )
            cursor.close()
        except Exception as e:
            self.logger.error(f"Error parsing articles for category {category}: {e}")
        return articles

    def get_source_name(self):
        return "News API"

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
