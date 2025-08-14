import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("news_aggregator.log"), logging.StreamHandler()],
)


class NewsService:
    def __init__(self, base_url, session, logger=None):
        self.base_url = base_url
        self.session = session
        self.logger = logger or logging.getLogger(__name__)

    def fetch_categories(self):
        try:
            res = requests.get(f"{self.base_url}/user/categories")
            data = res.json()
            if data.get("status") == "success":
                return ["all"] + data.get("categories", [])
            else:
                self.logger.warning("Failed to fetch categories from server response.")
                return ["all"]
        except Exception as e:
            self.logger.error(f"Error fetching categories: {e}")
            return ["all"]

    def get_today_headlines(self, category_choice):
        try:
            result = requests.get(
                f"{self.base_url}/user/headlines/today",
                params={"category": category_choice},
            )
            articles = result.json().get("articles", [])
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching today's headlines: {e}")
            return []

    def get_range_headlines(self, start, end, category_choice):
        try:
            result = requests.get(
                f"{self.base_url}/user/headlines/range",
                params={"from": start, "to": end, "category": category_choice},
            )
            articles = result.json().get("articles", [])
            return articles
        except Exception as e:
            self.logger.error(f"Error fetching range headlines: {e}")
            return []

    def save_article(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/user/articles/save",
                json={"email": self.session["email"], "article_id": article_id},
            )
            return result.json().get("message")
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error saving article: {e}")
            return "Error saving article."

    def delete_article(self, article_id):
        try:
            result = requests.delete(
                f"{self.base_url}/user/articles/saved/{article_id}",
                params={"email": self.session["email"]},
            )
            return result.json().get("message")
        except Exception as e:
            self.logger.error(f"Error deleting article: {e}")
            return "Error deleting article."

    def view_saved_articles(self):
        try:
            result = requests.get(
                f"{self.base_url}/user/articles/saved",
                params={"email": self.session["email"]},
            )
            articles = result.json().get("articles", [])
            return articles
        except Exception as e:
            self.logger.error(f"Error viewing saved articles: {e}")
            return []

    def search_articles(
        self, query, sort_by="published_at", start_date=None, end_date=None
    ):
        params = {
            "q": query,
            "sort_by": sort_by,
        }
        if start_date and end_date:
            params["from"] = start_date
            params["to"] = end_date
        try:
            res = requests.get(f"{self.base_url}/user/search", params=params)
            if res.status_code != 200:
                self.logger.warning(f"Search failed: {res.status_code}")
                return []
            articles = res.json().get("articles", [])
            return articles
        except Exception as e:
            self.logger.error(f"Error searching articles: {e}")
            return []

    def report_article(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/user/articles/report",
                json={"email": self.session["email"], "article_id": article_id},
            )
            return result.json().get("message")
        except Exception as e:
            self.logger.error(f"Error reporting article: {e}")
            return "Error reporting article."

    def like_article(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/user/feedback/like",
                json={"email": self.session["email"], "article_id": article_id},
            )
            return result.json().get("message")
        except Exception as e:
            self.logger.error(f"Error liking article: {e}")
            return "Error liking article."

    def dislike_article(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/user/feedback/dislike",
                json={"email": self.session["email"], "article_id": article_id},
            )
            return result.json().get("message")
        except Exception as e:
            self.logger.error(f"Error disliking article: {e}")
            return "Error disliking article."

    def view_personalized_articles(self):
        result = requests.get(
            f"{self.base_url}/user/personalized",
            params={"email": self.session["email"]},
        )

        if result.status_code != 200:
            print("Failed to fetch personalized articles.")
            return

        articles = result.json().get("articles", [])
        if not articles:
            print("No personalized articles found.")
            return

        for index, article in enumerate(articles, start=1):
            print(f"Article ID: {article['id']}")
            print(f"Article Title: {article['title']}")
            print(f"Article URL: {article['url']}")
            print()
