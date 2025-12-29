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
        data = {"article_id": article_id, "hide": True}
        response = requests.post(f"{self.base_url}/admin/articles/hide", json=data)
        if response.status_code == 200:
            return response.json().get("message", "Article hidden successfully.")
        else:
            return f"Failed to hide article: {response.text}"

    def unhide_article_visibility(self, article_id):
        data = {"article_id": article_id, "hide": False}
        response = requests.post(f"{self.base_url}/admin/articles/hide", json=data)
        if response.status_code == 200:
            return response.json().get("message", "Article unhidden successfully.")
        else:
            return f"Failed to unhide article: {response.text}"

    def get_hidden_categories(self):
        try:
            response = requests.get(f"{self.base_url}/admin/categories/hidden")
            if response.status_code == 200:
                return response.json().get("categories", [])
            else:
                return []
        except Exception as e:
            print(f"Error fetching hidden categories: {e}")
            return []

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
            data = {"keyword": keyword}
            response = requests.delete(
                f"{self.base_url}/admin/blocked_keywords", json=data
            )
            if response.status_code == 200:
                return f"Keyword '{keyword}' has been successfully unblocked."
            elif response.status_code == 404:
                return f"Keyword '{keyword}' is not currently blocked."
            else:
                return f"Failed to unblock keyword: {response.text}"
        except Exception as e:
            return f"Error removing blocked keyword: {e}"

    def get_blocked_keywords(self):
        try:
            res = requests.get(f"{self.base_url}/admin/blocked_keywords")
            data = res.json()
            return data.get("keywords", [])
        except Exception as e:
            self.logger.error(f"Failed to get blocked keywords: {e}")
            return []
