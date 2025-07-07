import requests
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("news_aggregator.log"), logging.StreamHandler()],
)


class NotificationService:

    def __init__(self, base_url, logger=None):
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)

    def get_notification_settings(self, email):
        try:
            response = requests.get(
                f"{self.base_url}/user/notifications",
                params={"email": email},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch notification settings: {e}")
            return {"categories": [], "keywords": []}

    def get_notifications_history(self, email):
        try:
            response = requests.get(
                f"{self.base_url}/user/notifications/history",
                params={"email": email},
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"Failed to fetch notifications history: {e}")
            return {"status": "error", "notifications": []}

    def toggle_category(self, email, category):
        try:
            response = requests.post(
                f"{self.base_url}/user/notifications/toggle",
                json={"email": email, "category": category},
            )
            return response.json().get("message", "Failed to toggle category.")
        except Exception as e:
            self.logger.error(f"Failed to toggle category: {e}")
            return "Failed to toggle category."

    def add_keyword(self, email, keyword):
        try:
            response = requests.post(
                f"{self.base_url}/user/notifications/keyword",
                json={"email": email, "keyword": keyword},
            )
            return response.json().get("message", "Failed to add keyword.")
        except Exception as e:
            self.logger.error(f"Failed to add keyword: {e}")
            return "Failed to add keyword."

    def remove_keyword(self, email, keyword):
        try:
            response = requests.delete(
                f"{self.base_url}/user/notifications/keyword",
                params={"email": email, "keyword": keyword},
            )
            return response.json().get("message", "Failed to remove keyword.")
        except Exception as e:
            self.logger.error(f"Failed to remove keyword: {e}")
            return "Failed to remove keyword."
