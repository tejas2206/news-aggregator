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
                print(f"{notification.get('sent_at')} - {notification.get('title')}\n")
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
