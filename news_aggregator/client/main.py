from datetime import datetime
import logging

from services.auth_handler import AuthService
from services.news_service import NewsService
from services.notification_service import NotificationService
from services.admin_service import AdminService
from cli.auth_ui import AuthUI
from cli.news_ui import NewsServiceUI
from cli.notification_ui import NotificationServiceUI
from cli.admin_ui import AdminServiceUI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("news_aggregator.log"), logging.StreamHandler()],
)

BASE_URL = "http://localhost:5000"
session = {}


def user_menu():
    news_service = NewsService(BASE_URL, session)
    news_ui = NewsServiceUI(news_service)
    notification_service = NotificationService(BASE_URL)
    notify_ui = NotificationServiceUI(notification_service, session)

    while True:
        print(
            f"\nWelcome to the News Application, {session['username']}! {datetime.now().strftime('%d-%b-%Y %I:%M%p')}"
        )
        print("1. Headlines")
        print("2. Saved Articles")
        print("3. Search")
        print("4. Notifications")
        print("5. Personalized Articles")
        print("6. Logout")
        choice = input("Choose: ")

        if choice == "1":
            news_ui.handle_headlines()
        elif choice == "2":
            news_ui.view_saved_articles()
        elif choice == "3":
            news_ui.search_articles()
        elif choice == "4":
            notify_ui.notifications_menu()
        elif choice == "5":
            news_service.view_personalized_articles()
        elif choice == "6":
            break
        else:
            print("Invalid choice. Try again.")


def admin_menu():
    admin_service = AdminService(BASE_URL)
    admin_ui = AdminServiceUI(admin_service)

    while True:
        print("\nAdmin Menu")
        print("1. View External Server Status")
        print("2. View External Server Details")
        print("3. Update External Server API Key")
        print("4. Add News Category")
        print("5. View Reported Articles")
        print("6. Toggle Category Visibility")
        print("7. Manage blocked keywords")
        print("8. Logout")

        choice = input("Choose: ").strip()
        if choice == "1":
            admin_ui.show_server_status()
        elif choice == "2":
            admin_ui.show_server_details()
        elif choice == "3":
            admin_ui.update_server_api_key()
        elif choice == "4":
            admin_ui.add_news_category()
        elif choice == "5":
            while True:
                admin_ui.show_reported_articles()
                print("\nReported Articles Actions:")
                print("1. Hide Article Visibility")
                print("2. Unhide Article Visibility")
                print("3. Back to Admin Menu")
                
                sub_choice = input("Choose: ").strip()
                if sub_choice == "1":
                    admin_ui.hide_article_visibility()
                elif sub_choice == "2":
                    admin_ui.unhide_article_visibility()
                elif sub_choice == "3":
                    break
                else:
                    print("Invalid choice. Please try again.")
        elif choice == "6":
            admin_ui.show_hidden_categories()
            admin_ui.toggle_category_visibility()
        elif choice == "7":
            admin_ui.manage_blocked_keywords()
        elif choice == "8":
            print("Logging out of admin dashboard.")
            break
        else:
            print("Invalid choice. Please try again.")


def main():
    auth_service = AuthService(BASE_URL)
    auth_ui = AuthUI(auth_service, session)

    while True:
        print(
            "\nWelcome to the News Aggregator application. Please choose the options below."
        )
        print("1. Login")
        print("2. Sign Up")
        print("3. Exit")

        choice = input("Choose: ").strip()
        if choice == "1":
            result = auth_ui.login()
            if result:
                if session["role"] == "admin":
                    admin_menu()
                else:
                    user_menu()
        elif choice == "2":
            auth_ui.signup()
        elif choice == "3":
            print("Exiting News Aggregator.")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
