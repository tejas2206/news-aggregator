import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("news_aggregator.log"), logging.StreamHandler()],
)


class AdminService:
    def __init__(self, base_url, logger=None):
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)

    def get_server_status(self):
        try:
            response = requests.get(f"{self.base_url}/admin/servers/status")
            response.raise_for_status()
            data = response.json()
            return data.get("servers", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch server status: {e}")
            return []

    def get_server_details(self):
        try:
            response = requests.get(f"{self.base_url}/admin/servers/details")
            response.raise_for_status()
            data = response.json()
            return data.get("servers", [])
        except Exception as e:
            self.logger.error(f"Failed to fetch server details: {e}")
            return []

    def update_server_api_key(self, server_id, new_key):
        try:
            response = requests.post(
                f"{self.base_url}/admin/servers/update",
                json={"server_id": server_id, "api_key": new_key},
            )
            return response.json().get("message")
        except Exception as e:
            self.logger.error(f"Failed to update API key: {e}")
            return "Failed to update API key."

    def add_news_category(self, name):
        try:
            response = requests.post(
                f"{self.base_url}/admin/categories/add", json={"name": name}
            )
            return response.json().get("message")
        except Exception as e:
            self.logger.error(f"Failed to add category: {e}")
            return "Failed to add category."

    def get_reported_articles(self):
        try:
            result = requests.get(f"{self.base_url}/admin/reports")
            data = result.json()
            if data["status"] == "success":
                return data["reports"]
            else:
                self.logger.warning("Failed to load reported articles.")
                return []
        except Exception as e:
            self.logger.error(f"Error loading reported articles: {e}")
            return []

    def hide_article_visibility(self, article_id):
        try:
            result = requests.post(
                f"{self.base_url}/admin/articles/hide", json={"article_id": article_id}
            )
            return result.json().get("message")
        except Exception as e:
            self.logger.error(f"Failed to hide article: {e}")
            return "Failed to hide article."

    def toggle_category_visibility(self, category):
        try:
            result = requests.post(
                f"{self.base_url}/admin/categories/toggle", json={"category": category}
            )
            data = result.json()
            return data.get("message", "Error toggling category.")
        except Exception as e:
            self.logger.error(f"Failed to toggle category: {e}")
            return "Error toggling category."

    def add_blocked_keyword(self, keyword):
        try:
            res = requests.post(
                f"{self.base_url}/admin/blocked_keywords", json={"keyword": keyword}
            )
            return res.json().get("message")
        except Exception as e:
            self.logger.error(f"Failed to add blocked keyword: {e}")
            return "Failed to add blocked keyword."

    def remove_blocked_keyword(self, keyword):
        try:
            res = requests.delete(
                f"{self.base_url}/admin/blocked_keywords", params={"keyword": keyword}
            )
            return res.json().get("message")
        except Exception as e:
            self.logger.error(f"Failed to remove blocked keyword: {e}")
            return "Failed to remove blocked keyword."

    def get_blocked_keywords(self):
        try:
            res = requests.get(f"{self.base_url}/admin/blocked_keywords")
            data = res.json()
            return data.get("keywords", [])
        except Exception as e:
            self.logger.error(f"Failed to get blocked keywords: {e}")
            return []


class AdminServiceUI:
    def __init__(self, admin_service):
        self.admin_service = admin_service

    def show_server_status(self):
        servers = self.admin_service.get_server_status()
        print("\nList of External Servers:")
        for server in servers:
            print(
                f"{server['id']}. {server['name']} - {server['status']} - Last Accessed: {server['last_accessed']}"
            )

    def show_server_details(self):
        servers = self.admin_service.get_server_details()
        print("\nExternal Server API Keys:")
        for server in servers:
            print(f"{server['id']}. {server['name']} - API KEY: {server['api_key']}")

    def update_server_api_key(self):
        server_id = input("Enter the External Server ID: ").strip()
        new_key = input("Enter the New API Key: ").strip()
        message = self.admin_service.update_server_api_key(server_id, new_key)
        print(message)

    def add_news_category(self):
        name = input("Enter New Category Name: ").strip()
        message = self.admin_service.add_news_category(name)
        print(message)

    def show_reported_articles(self):
        articles = self.admin_service.get_reported_articles()
        if not articles:
            print("No articles reported.")
            return
        print("\nReported Articles:\n")
        for article in articles:
            print(f"ID: {article['id']} | Reports: {article['report_count']}")
            print(f"Title: {article['title']}")

    def hide_article_visibility(self):
        article_id = input("Enter Article ID to hide: ")
        message = self.admin_service.hide_article_visibility(article_id)
        print(message)

    def toggle_category_visibility(self):
        category = input("Enter category to toggle visibility: ").strip().lower()
        message = self.admin_service.toggle_category_visibility(category)
        print(message)

    def manage_blocked_keywords(self):
        while True:
            print("\n1. Add Blocked Keyword")
            print("2. Remove Blocked Keyword")
            print("3. View Blocked Keywords")
            print("4. Back")
            choice = input("Choose: ")
            if choice == "1":
                keyword = input("Enter keyword to block: ").strip().lower()
                message = self.admin_service.add_blocked_keyword(keyword)
                print(message)
            elif choice == "2":
                keyword = input("Enter keyword to unblock: ").strip().lower()
                message = self.admin_service.remove_blocked_keyword(keyword)
                print(message)
            elif choice == "3":
                keywords = self.admin_service.get_blocked_keywords()
                print("Blocked Keywords:", ", ".join(keywords))
            elif choice == "4":
                break
