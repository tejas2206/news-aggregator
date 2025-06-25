import requests
from datetime import datetime


class NewsService:
    def __init__(self, base_url, session):
        self.base_url = base_url
        self.session = session

    def get_category_map(self):
        return {
            "1": "all",
            "2": "business",
            "3": "entertainment",
            "4": "sports",
            "5": "technology",
        }

    def show_categories(self):
        category_map = self.get_category_map()
        for key, value in category_map.items():
            print(f"{key}. {value.title()}")
        return category_map

    def display_articles(self, articles):
        if not articles:
            print("No articles found.")
        for article in articles:
            article_id = article.get("id") or article.get("article_id") or "?"
            # print(f"{article_id}. [{article.get('category', 'general')}] {article['title']} ({article['url']})")
            print(
                f"{article_id}. {article['title']} [{article.get('category', 'general')}]"
            )
            print("------------------------------------------------------")

    def get_today_headlines(self):
        print("\nPlease choose the options below for Headlines")
        category_map = self.show_categories()
        category_choice = category_map.get(input("Choose: "), "all")
        result = requests.get(
            f"{self.base_url}/user/headlines/today",
            params={"category": category_choice},
        )
        articles = result.json().get("articles", [])
        print("\nH E A D L I N E S\n")
        self.display_articles(articles)
        self.handle_article_options()

    def get_range_headlines(self):
        start = input("Start Date (YYYY-MM-DD): ")
        end = input("End Date (YYYY-MM-DD): ")
        print("\nChoose category:\n")
        category_map = self.show_categories()
        category_choice = category_map.get(input("Choose: "), "all")
        result = requests.get(
            f"{self.base_url}/user/headlines/range",
            params={"from": start, "to": end, "category": category_choice},
        )
        articles = result.json().get("articles", [])
        print("\nH E A D L I N E S\n")
        self.display_articles(articles)
        self.handle_article_options()

    def save_article(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/user/articles/save",
                json={"email": self.session["email"], "article_id": article_id},
            )
            print(result.json().get("message"))
        except requests.exceptions.RequestException as e:
            print("Error saving article:", str(e))

    def delete_article(self, article_id):
        result = requests.delete(
            f"{self.base_url}/user/articles/saved/{article_id}",
            params={"email": self.session["email"]},
        )
        print(result.json().get("message"))

    def view_saved_articles(self):
        result = requests.get(
            f"{self.base_url}/user/articles/saved",
            params={"email": self.session["email"]},
        )
        articles = result.json().get("articles", [])
        print("\nS A V E D  A R T I C L E S\n2")
        self.display_articles(articles)
        print("\n1. Delete Article\n2. Back")
        if input("Choose: ").strip() == "1":
            article_id = input("Enter Article ID to delete: ").strip()
            self.delete_article(article_id)

    def search_articles(self):
        print("\nS E A R C H\n")
        query = input("Enter search keyword: ")
        result = requests.get(f"{self.base_url}/user/search", params={"q": query})
        articles = result.json().get("articles", [])
        self.display_articles(articles)
        print("\n1. Save Article\n2. Back")
        if input("Choose: ").strip() == "1":
            article_id = input("Enter Article ID to save: ").strip()
            self.save_article(article_id)

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

    def handle_article_options(self):
        while True:
            print("\n1. Save Article\n2. Report Article\n3. Like\n4. Dislike\n5. Back")
            choice = input("Choose: ").strip()
            if choice == "1":
                article_id = input("Enter Article ID to save: ").strip()
                self.save_article(article_id)
            elif choice == "2":
                article_id = input("Enter Article ID to report: ").strip()
                self.report_article(article_id)
            elif choice == "3":
                article_id = input("Enter Article ID to like: ").strip()
                self.like_article(article_id)
            elif choice == "4":
                article_id = input("Enter Article ID to dislike: ").strip()
                self.dislike_article(article_id)
            elif choice == "5":
                break

    def report_article(self, article_id):
        result = requests.post(f"{self.base_url}/user/articles/report", json={
            "email": self.session["email"], "article_id": article_id
        })
        print(result.json().get("message"))

    def like_article(self, article_id):
        result = requests.post(f"{self.base_url}/user/feedback/like", json={
            "email": self.session["email"],
            "article_id": article_id
        })
        print(result.json().get("message"))

    def dislike_article(self, article_id):
        result = requests.post(f"{self.base_url}/user/feedback/dislike", json={
            "email": self.session["email"],
            "article_id": article_id
        })
        print(result.json().get("message"))
