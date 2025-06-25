import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
from server.db.database import get_db

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)


class NewsFetcher:
    def __init__(self):
        self.newsapi_key = os.getenv("NEWS_API_KEY")
        self.thenewsapi_key = os.getenv("THE_NEWS_API_KEY")

    def fetch_from_newsapi(self):
        if not self.newsapi_key:
            print("NEWS_API_KEY not configured.")
            return []

        url = f"https://newsapi.org/v2/top-headlines?language=en&pageSize=10&apiKey={self.newsapi_key}"
        result = requests.get(url)
        if result.status_code != 200:
            print("NewsAPI failed:", result.status_code)
            return []

        return self._parse_newsapi(result.json())

    def fetch_from_thenewsapi(self):
        if not self.thenewsapi_key:
            print("THE_NEWS_API_KEY not configured.")
            return []

        url = f"https://api.thenewsapi.com/v1/news/top?language=en&api_token={self.thenewsapi_key}"
        result = requests.get(url)
        if result.status_code != 200:
            print("TheNewsAPI failed:", result.status_code)
            return []

        return self._parse_thenewsapi(result.json())

    def _categorize_article(self, text):
        text = text.lower()
        if any(
            keyword in text
            for keyword in [
                "cricket",
                "football",
                "nba",
                "match",
                "goal",
                "tournament",
                "sports",
            ]
        ):
            return "sports"
        if any(
            keyword in text
            for keyword in [
                "business",
                "economy",
                "finance",
                "stock",
                "market",
                "invest",
            ]
        ):
            return "business"
        if any(
            keyword in text
            for keyword in [
                "movie",
                "music",
                "celebrity",
                "tv",
                "entertainment",
                "show",
            ]
        ):
            return "entertainment"
        if any(
            keyword in text
            for keyword in [
                "ai ",
                "software ",
                "hardware",
                "tech",
                "gadget",
                "technology",
            ]
        ):
            return "technology"
        return "general"

    def _parse_newsapi(self, data):
        articles = []
        for article in data.get("articles", []):
            category_name = self._categorize_article(
                article.get("title", "") + " " + (article.get("description") or "")
            )
            category_id = self._get_or_create_category(category_name)

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
        return articles

    def _parse_thenewsapi(self, data):
        articles = []
        for article in data.get("data", []):
            raw_category = article.get("category") or article.get("categories")
            if isinstance(raw_category, str):
                category = raw_category
            elif isinstance(raw_category, list) and raw_category:
                category = raw_category[0]
            else:
                category = "general"

            category_id = self._get_or_create_category(category)

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
        return articles

    def _get_or_create_category(self, name):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
        row = cursor.fetchone()
        if row:
            return row[0]
        cursor.execute("INSERT INTO categories (name) VALUES (%s)", (name,))
        conn.commit()
        return cursor.lastrowid

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
