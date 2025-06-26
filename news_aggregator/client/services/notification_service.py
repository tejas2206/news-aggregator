import requests


class NotificationServiceCLI:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    # def view_notifications(self):
    #     result = requests.get(
    #         f"{self.base_url}/user/notifications",
    #         params={"email": self.session["email"]},
    #     )
    #     data = result.json()
    #     print("\nC O N F I G U R E - N O T I F I C A T I O N S\n")
    #     print("Categories:")
    #     for item in data.get("categories", []):
    #         status = "Enabled" if item["enabled"] else "Disabled"
    #         print(f" - {item['category']}: {status}")
    #     print("Keywords:", ", ".join(data.get("keywords", [])))

    def view_notifications(self):
        email = self.session["email"]
        res = requests.get(f"{self.base_url}/user/notifications/history", params={"email": email})
        data = res.json()

        if data["status"] == "success":
            print("\nSent Notifications:")
            for n in data["notifications"]:
                print(f"{n['sent_at']} - {n['title']}")
                print(f"URL: {n['url']}")
                # print(f"Message: {n['message']}\n")
        else:
            print("Failed to fetch notifications.")


    def configure_notifications(self):
        self.view_notifications()
        print("\nC O N F I G U R E - N O T I F I C A T I O N S\n")
        print("\n1. Enable Category\n2. Add Keyword\n3. Remove Keyword\n4. Back")
        option = input("Choose: ")

        if option == "1":
            category = input("Enter category to toggle: ").lower()
            result = requests.post(
                f"{self.base_url}/user/notifications/toggle",
                json={"email": self.session["email"], "category": category},
            )
            print(result.json().get("message"))

        elif option == "2":
            keyword = input("Enter keyword to add: ")
            result = requests.post(
                f"{self.base_url}/user/notifications/keyword",
                json={"email": self.session["email"], "keyword": keyword},
            )
            print(result.json().get("message"))

        elif option == "3":
            keyword = input("Enter keyword to remove: ")
            result = requests.delete(
                f"{self.base_url}/user/notifications/keyword",
                params={"email": self.session["email"], "keyword": keyword},
            )
            print(result.json().get("message"))

    def notifications_menu(self):
        while True:
            print("\nN O T I F I C A T I O N S\n")
            print("1. View Notifications")
            print("2. Configure Notifications")
            print("3. Back")
            choice = input("Choose: ")
            if choice == "1":
                self.view_notifications()
            elif choice == "2":
                self.configure_notifications()
            elif choice == "3":
                break
