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


class NotificationServiceUI:

    def __init__(self, notification_service, session):
        self.notification_service = notification_service
        self.session = session

    def show_notification_settings(self):
        data = self.notification_service.get_notification_settings(
            self.session["email"]
        )
        print("Categories:")
        for item in data.get("categories", []):
            status = "Enabled" if item.get("enabled") else "Disabled"
            print(f" - {item.get('category')}: {status}")
        print("Keywords:", ", ".join(data.get("keywords", [])))

    def show_notifications_history(self):
        data = self.notification_service.get_notifications_history(
            self.session["email"]
        )
        if data.get("status") == "success":
            print("\nSent Notifications:")
            for notification in data.get("notifications", []):
                print(f"{notification.get('sent_at')} - {notification.get('title')}")
        else:
            print("Failed to fetch notifications.")

    def configure_notifications(self):
        print("\nC O N F I G U R E - N O T I F I C A T I O N S\n")
        self.show_notification_settings()
        print("\n1. Toggle Category\n2. Add Keyword\n3. Remove Keyword\n4. Back")
        option = input("Choose: ")

        if option == "1":
            category = input("Enter category to toggle: ").lower()
            message = self.notification_service.toggle_category(
                self.session["email"], category
            )
            print(message)
        elif option == "2":
            keyword = input("Enter keyword to add: ")
            message = self.notification_service.add_keyword(
                self.session["email"], keyword
            )
            print(message)
        elif option == "3":
            keyword = input("Enter keyword to remove: ")
            message = self.notification_service.remove_keyword(
                self.session["email"], keyword
            )
            print(message)

    def notifications_menu(self):
        while True:
            print("\nN O T I F I C A T I O N S\n")
            print("1. View Notifications")
            print("2. Configure Notifications")
            print("3. Back")
            choice = input("Choose: ")
            if choice == "1":
                self.show_notifications_history()
            elif choice == "2":
                self.configure_notifications()
            elif choice == "3":
                break
