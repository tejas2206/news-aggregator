class NewsServiceUI:
    def __init__(self, news_service):
        self.news_service = news_service

    def show_categories(self):
        categories = self.news_service.fetch_categories()
        category_map = {str(index + 1): category for index, category in enumerate(categories)}
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
                f"Article ID: {article_id}\nArticle title: {article['title']}\nArticle Category: {article.get('category', 'general')}\nArticle URL: ({article['url']})"
            )
            print("-" * 30)

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
        for article in articles:
            print(f"ID: {article['id']}")
            print(f"Title: {article['title']}")
            print(f"Source: {article['source']}")
            print(f"Published: {article['published_at']}")
            print(f"Category: {article['category']}")
            print(f"Likes: {article['likes']}, Dislikes: {article['dislikes']}")
            print(f"URL: {article['url']}")
            print("-" * 30)
        self.handle_article_options()

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
