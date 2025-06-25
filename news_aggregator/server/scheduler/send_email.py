from server.services.notification_service import NotificationService
from server.services.news_fetcher import NewsFetcher
from server.db.database import get_db


class NotificationRunner:
    def __init__(self):
        self.notifier = NotificationService()
        self.fetcher = NewsFetcher()

    def resolve_categories(self, articles):
        conn = get_db()
        cursor = conn.cursor()
        for article in articles:
            category_id = article.get("category_id")
            if category_id:
                cursor.execute("SELECT name FROM categories WHERE id = %s", (category_id,))
                row = cursor.fetchone()
                article["category"] = row[0] if row else "general"
            else:
                article["category"] = "general"
        cursor.close()

    def run(self):
        print("[INFO] Fetching articles for notification...")
        articles_newsapi = self.fetcher.fetch_from_newsapi()
        articles_thenewsapi = self.fetcher.fetch_from_thenewsapi()
        all_articles = articles_newsapi + articles_thenewsapi

        if not all_articles:
            print("[INFO] No articles fetched. Skipping notification.")
            return

        print(f"[INFO] Sending notifications for {len(all_articles)} articles...")
        self.notifier.notify_users_about_articles(all_articles)
        print("[SUCCESS] Notification process completed.")


if __name__ == "__main__":
    runner = NotificationRunner()
    runner.run()
