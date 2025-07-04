import requests


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

        params = {
            "q": query,
            "sort_by": sort_by,
        }
        if start_date and end_date:
            params["from"] = start_date
            params["to"] = end_date

        res = requests.get(f"{self.base_url}/user/search", params=params)

        if res.status_code != 200:
            print("Search failed:", res.status_code)
            return

        articles = res.json().get("articles", [])
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
