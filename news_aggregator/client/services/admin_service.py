import requests


class AdminService:
    def __init__(self, base_url):
        self.base_url = base_url

    def view_server_status(self):
        try:
            response = requests.get(f"{self.base_url}/admin/servers/status")
            response.raise_for_status()
            data = response.json()
            print("\nList of External Servers:")
            for server in data.get("servers", []):
                print(
                    f"{server['id']}. {server['name']} - {server['status']} - Last Accessed: {server['last_accessed']}"
                )
        except Exception as e:
            print("Failed to fetch server status:", str(e))

    def view_server_details(self):
        try:
            response = requests.get(f"{self.base_url}/admin/servers/details")
            response.raise_for_status()
            data = response.json()
            print("\nExternal Server API Keys:")
            for server in data.get("servers", []):
                print(
                    f"{server['id']}. {server['name']} - API KEY: {server['api_key']}"
                )
        except Exception as e:
            print("Failed to fetch server details:", str(e))

    def update_server_api_key(self):
        server_id = input("Enter the External Server ID: ").strip()
        new_key = input("Enter the New API Key: ").strip()
        try:
            response = requests.post(
                f"{self.base_url}/admin/servers/update",
                json={"server_id": server_id, "api_key": new_key},
            )
            print(response.json().get("message"))
        except Exception as e:
            print("Failed to update API key:", str(e))

    def add_news_category(self):
        name = input("Enter New Category Name: ").strip()
        try:
            response = requests.post(
                f"{self.base_url}/admin/categories/add", json={"name": name}
            )
            print(response.json().get("message"))
        except Exception as e:
            print("Failed to add category:", str(e))

    def view_reported_articles(self):
        result = requests.get(f"{self.base_url}/admin/reports")
        try:
            data = result.json()
            if data["status"] == "success":
                articles = data["reports"]
                if not articles:
                    print("No articles reported.")
                    return
                print("\nReported Articles:\n")
                for article in articles:
                    print(f"ID: {article['id']} | Reports: {article['report_count']}")
                    print(f"Title: {article['title']}")
            else:
                print("Failed to load reported articles.")
        except Exception as e:
            print("Error:", e)


    def hide_article_visibility(self):
        article_id = input("Enter Article ID to hide: ")
        result = requests.post(f"{self.base_url}/admin/articles/hide", json={"article_id": article_id})
        print(result.json().get("message"))

    def toggle_category_visibility(self):
        category = input("Enter category to toggle visibility: ").strip().lower()
        result = requests.post(
            f"{self.base_url}/admin/categories/toggle",
            json={"category": category}
        )
        data = result.json()
        print(data.get("message", "Error toggling category."))
