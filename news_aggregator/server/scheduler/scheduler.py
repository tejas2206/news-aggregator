import schedule
import time
from datetime import datetime
import importlib
import pkgutil
from server.db.database import get_db
from server.sources.base_source import NewsSource
from server.services.notification_service import NotificationService
from server import sources


class NewsScheduler:
    def __init__(self):
        self.fetchers = self._load_fetchers()
        self.notifier = NotificationService()

    def run(self):
        """
        Start the scheduler: run once immediately, then every 4 hours.
        """
        self._fetch_and_process_articles()
        schedule.every(4).hours.do(self._fetch_and_process_articles)
        print("Scheduler is active. It will run every 4 hours.")
        while True:
            schedule.run_pending()
            time.sleep(60)

    def _load_fetchers(self):
        """
        Dynamically load all classes that inherit from NewsSource in the sources package.
        """
        fetchers = []

        for _, module_name, _ in pkgutil.iter_modules(sources.__path__):
            module = importlib.import_module(f"server.sources.{module_name}")
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and issubclass(attr, NewsSource) and attr is not NewsSource:
                    fetchers.append(attr())
                    print(f"[PLUGIN LOADED] {attr.__name__} from {module_name}")

        return fetchers

    def _fetch_and_process_articles(self):
        print("\n[INFO] Running scheduled fetch and notification...")
        all_articles = []

        for fetcher in self.fetchers:
            source_name = fetcher.get_source_name()
            all_articles += self._fetch_and_store(source_name, fetcher.fetch_articles)

        self._resolve_categories_for_notification(all_articles)
        self.notifier.notify_users_about_articles(all_articles)

    def _fetch_and_store(self, source_name, fetch_function):
        try:
            articles = fetch_function()
            saved_count = self._save_articles_to_db(articles)
            self._update_server_status(source_name, True)
            print(f"[SUCCESS] {saved_count} articles saved from {source_name}")
            return articles
        except Exception as error:
            print(f"[ERROR] Failed to fetch from {source_name}: {error}")
            self._update_server_status(source_name, False)
            return []

    # def _save_articles_to_db(self, articles):
    #     conn = get_db()
    #     cursor = conn.cursor()

    #     insert_query = """
    #         INSERT INTO news_articles 
    #         (external_id, title, content, url, source, category_id, published_at)
    #         VALUES (%s, %s, %s, %s, %s, %s, %s)
    #         ON DUPLICATE KEY UPDATE 
    #             title = VALUES(title), 
    #             content = VALUES(content)
    #     """

    #     count = 0
    #     for article in articles:
    #         try:
    #             cursor.execute(
    #                 insert_query,
    #                 (
    #                     article.get("external_id"),
    #                     article.get("title"),
    #                     article.get("content"),
    #                     article.get("url"),
    #                     article.get("source"),
    #                     article.get("category_id"),
    #                     article.get("published_at"),
    #                 ),
    #             )
    #             count += 1
    #         except Exception as e:
    #             print(f"[WARNING] Skipped article: {e}")

    #     conn.commit()
    #     cursor.close()
    #     return count

    def _save_articles_to_db(self, articles):
        conn = get_db()
        cursor = conn.cursor()

        insert_query = """
            INSERT INTO news_articles 
            (external_id, title, content, url, source, category_id, published_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
                title = VALUES(title), 
                content = VALUES(content),
                id = LAST_INSERT_ID(id)  -- Ensures we always get the current ID
        """

        select_query = "SELECT id FROM news_articles WHERE external_id = %s"

        count = 0
        for article in articles:
            try:
                cursor.execute(
                    insert_query,
                    (
                        article.get("external_id"),
                        article.get("title"),
                        article.get("content"),
                        article.get("url"),
                        article.get("source"),
                        article.get("category_id"),
                        article.get("published_at"),
                    ),
                )
                conn.commit()
                cursor.execute(select_query, (article.get("external_id"),))
                result = cursor.fetchone()
                if result:
                    article["id"] = result[0]
                count += 1
            except Exception as e:
                print(f"[WARNING] Skipped article: {e}")

        cursor.close()
        return count


    def _update_server_status(self, server_name, is_active):
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            """
            UPDATE external_servers
            SET status = %s, last_accessed = %s
            WHERE name = %s
        """,
            ("Active" if is_active else "Not Active", datetime.now(), server_name),
        )
        conn.commit()
        cursor.close()

    def _resolve_categories_for_notification(self, articles):
        conn = get_db()
        cursor = conn.cursor()
        for article in articles:
            category_id = article.get("category_id")
            if category_id:
                cursor.execute(
                    "SELECT name FROM categories WHERE id = %s", (category_id,)
                )
                result = cursor.fetchone()
                article["category"] = result[0] if result else "general"
            else:
                article["category"] = "general"
        cursor.close()


if __name__ == "__main__":
    scheduler = NewsScheduler()
    scheduler.run()
