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
            print(
                f"ID: {article['id']} | Reports: {article['report_count']} | Hidden status: {article['is_hidden']}"
            )
            print(f"Title: {article['title']}\n")

    def hide_article_visibility(self):
        article_id = input("Enter Article ID to hide: ")
        message = self.admin_service.hide_article_visibility(article_id)
        print(message)

    def unhide_article_visibility(self):
        article_id = input("Enter Article ID to unhide: ")
        message = self.admin_service.unhide_article_visibility(article_id)
        print(message)

    def show_hidden_categories(self):
        categories = self.admin_service.get_hidden_categories()
        if not categories:
            print("\nNo categories are currently hidden.")
            return

        print("\nCurrently Hidden Categories:")
        for category in categories:
            print(f"- {category['name']}")

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
