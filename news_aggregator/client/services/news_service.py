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
        res = requests.get(
            f"{self.base_url}/user/personalized",
            params={"email": self.session["email"]}
        )

        if res.status_code != 200:
            print("Failed to fetch personalized articles.")
            return

        articles = res.json().get("articles", [])
        if not articles:
            print("No personalized articles found.")
            return

        for idx, article in enumerate(articles, start=1):
            print(f"{idx}. {article['title']}")
            print(f"   URL: {article['url']}")
            print(f"   Category: {article['category']}")
            print()


class NewsServiceUI:
    def __init__(self, news_service):
        self.news_service = news_service

    def show_categories(self):
        categories = self.news_service.fetch_categories()
        category_map = {str(i + 1): cat for i, cat in enumerate(categories)}
        for key, value in category_map.items():
            print(f"{key}. {value.title()}")
        return category_map

    def display_articles(self, articles):
        if not articles:
            print("No articles found.")
            return
        for article in articles:
            article_id = article.get("id") or article.get("article_id") or "?"
            print(
                f"Article ID: {article_id}\nArticle_title: {article['title']}\nArticle Category: {article.get('category', 'general')}\nArticle URL: ({article['url']})"
            )
            print("------------------------------------------------------")

    def view_saved_articles(self):
        articles = self.news_service.view_saved_articles()
        print("\nS A V E D  A R T I C L E S\n")
        self.display_articles(articles)
        print("\n1. Delete Article\n2. Back")
        if input("Choose: ").strip() == "1":
            article_id = input("Enter Article ID to delete: ").strip()
            message = self.news_service.delete_article(article_id)
            print(message)

    def search_articles(self):
        query = input("Enter search query: ").strip()
        filter_date = input("Filter by date range? (y/n): ").strip().lower()
        start_date = end_date = None
        if filter_date == "y":
            start_date = input("From date (YYYY-MM-DD): ").strip()
            end_date = input("To date (YYYY-MM-DD): ").strip()
        elif filter_date == "n":
            print("Skipping date filter.")
        else:
            print("Invalid input. Skipping date filter.")
        print("Sort by:")
        print("1. Published date")
        print("2. Likes descending")
        print("3. Dislikes descending")
        sort_choice = input("Choose option: ").strip()
        if sort_choice == "2":
            sort_by = "likes"
        elif sort_choice == "3":
            sort_by = "dislikes"
        else:
            sort_by = "published_at"
        articles = self.news_service.search_articles(
            query, sort_by, start_date, end_date
        )
        if not articles:
            print("No articles found.")
            return
        print("\nSearch Results:\n")
        for art in articles:
            print(f"ID: {art['id']}")
            print(f"Title: {art['title']}")
            print(f"Source: {art['source']}")
            print(f"Published: {art['published_at']}")
            print(f"Category: {art['category']}")
            print(f"Likes: {art['likes']}, Dislikes: {art['dislikes']}")
            print(f"URL: {art['url']}")
            print("-" * 50)

    def handle_headlines(self):
        print("\nH E A D L I N E S\n")
        print("\n1. Today\n2. Date Range\n3. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            self.get_today_headlines()
        elif choice == "2":
            self.get_range_headlines()
        elif choice == "3":
            return
        
    def get_today_headlines(self):
        print("\nChoose category:\n")
        category_map = self.show_categories()
        category_choice = category_map.get(input("Choose: "), "all")
        articles = self.news_service.get_today_headlines(category_choice)
        print("\nH E A D L I N E S\n")
        self.display_articles(articles)
        self.handle_article_options()

    def get_range_headlines(self):
        start = input("Start Date (YYYY-MM-DD): ")
        end = input("End Date (YYYY-MM-DD): ")
        print("\nChoose category:\n")
        category_map = self.show_categories()
        category_choice = category_map.get(input("Choose: "), "all")
        articles = self.news_service.get_range_headlines(start, end, category_choice)
        print("\nH E A D L I N E S\n")
        self.display_articles(articles)
        self.handle_article_options()

    def handle_article_options(self):
        while True:
            print("\n1. Save Article\n2. Report Article\n3. Like\n4. Dislike\n5. Back")
            choice = input("Choose: ").strip()
            if choice == "1":
                article_id = input("Enter Article ID to save: ").strip()
                message = self.news_service.save_article(article_id)
                print(message)
            elif choice == "2":
                article_id = input("Enter Article ID to report: ").strip()
                message = self.news_service.report_article(article_id)
                print(message)
            elif choice == "3":
                article_id = input("Enter Article ID to like: ").strip()
                message = self.news_service.like_article(article_id)
                print(message)
            elif choice == "4":
                article_id = input("Enter Article ID to dislike: ").strip()
                message = self.news_service.dislike_article(article_id)
                print(message)
            elif choice == "5":
                break
