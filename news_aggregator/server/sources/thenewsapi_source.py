import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from server.db.database import get_db
from server.sources.base_source import NewsSource

load_dotenv(Path(__file__).resolve().parents[2] / ".env")


class TheNewsAPISource(NewsSource):
    def __init__(self):
        self.api_key = os.getenv("THE_NEWS_API_KEY")

    def fetch_articles(self):
        if not self.api_key:
            print("THE_NEWS_API_KEY not configured.")
            return []

        url = f"https://api.thenewsapi.com/v1/news/top?language=en&api_token={self.api_key}"
        result = requests.get(url)
        if result.status_code != 200:
            print("TheNewsAPI failed:", result.status_code)
            return []

        return self._parse_articles(result.json())

    def _parse_articles(self, data):
        conn = get_db()
        cursor = conn.cursor()
        articles = []

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
        return articles

    def get_source_name(self):
        return "The News API"

    def _parse_date(self, raw):
        try:
            return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%S.%fZ").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        except:
            try:
                return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except:
                return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
