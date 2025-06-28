from datetime import datetime
from services.auth_handler import AuthHandler
from services.news_service import NewsService
from services.notification_service import NotificationServiceCLI
from services.admin_service import AdminService

BASE_URL = "http://localhost:5000"
session = {}


def user_menu():
    news = NewsService(BASE_URL, session)
    notify = NotificationServiceCLI(session, BASE_URL)

    while True:
        print(
            f"\nWelcome to the News Application, {session['username']}! {datetime.now().strftime('%d-%b-%Y %I:%M%p')}"
        )
        print("1. Headlines")
        print("2. Saved Articles")
        print("3. Search")
        print("4. Notifications")
        print("5. Logout")
        choice = input("Choose: ")

        if choice == "1":
            news.handle_headlines()
        elif choice == "2":
            news.view_saved_articles()
        elif choice == "3":
            news.search_articles()
        elif choice == "4":
            notify.notifications_menu()
        elif choice == "5":
            break
        else:
            print("Invalid choice. Try again.")


def admin_menu():
    admin = AdminService(BASE_URL)

    while True:
        print("\nAdmin Menu")
        print("1. View External Server Status")
        print("2. View External Server Details")
        print("3. Update External Server API Key")
        print("4. Add News Category")
        print("5. View Reported Articles")
        print("6. Hide Article Visibility")
        print("7. Toggle Category Visibility")
        print("8. Logout")

        choice = input("Choose: ").strip()
        if choice == "1":
            admin.view_server_status()
        elif choice == "2":
            admin.view_server_details()
        elif choice == "3":
            admin.update_server_api_key()
        elif choice == "4":
            admin.add_news_category()
        elif choice == "5":
            admin.view_reported_articles()
        elif choice == "6":
            admin.hide_article_visibility()
        elif choice == "7":
            admin.toggle_category_visibility()
        elif choice == "8":
            print("Logging out of admin dashboard.")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    auth = AuthHandler(session, BASE_URL)

    while True:
        print(
            "\nWelcome to the News Aggregator application. Please choose the options below."
        )
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")

        choice = input("Choose: ").strip()
        if choice == "1":
            result = auth.login()
            if result:
                if session["role"] == "admin":
                    admin_menu()
                else:
                    user_menu()
        elif choice == "2":
            auth.signup()
        elif choice == "3":
            print("Exiting News Aggregator.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
