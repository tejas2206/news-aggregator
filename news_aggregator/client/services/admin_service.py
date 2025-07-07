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
