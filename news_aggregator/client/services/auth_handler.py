import re
import requests
import getpass
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler("news_aggregator.log"), logging.StreamHandler()],
)


class AuthService:
    def __init__(self, base_url, logger=None):
        self.base_url = base_url
        self.logger = logger or logging.getLogger(__name__)

    def is_valid_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def is_valid_password(self, password):
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"

        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one capital letter"

        if not re.search(r"\d", password):
            return False, "Password must contain at least one digit"

        special_chars = r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]'
        if not re.search(special_chars, password):
            return False, "Password must contain special character"

        return True, "Password is valid"

    def signup(self, username, email, password):
        is_valid, validation_message = self.is_valid_password(password)
        if not is_valid:
            return validation_message

        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json={"username": username, "email": email, "password": password},
            )
            response.raise_for_status()
            return response.json().get("message", "Signup successful.")
        except Exception as e:
            self.logger.error(f"Signup error: {e}")
            return f"Signup error: {e}"

    def login(self, email, password):
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
            )
            data = response.json()
            if response.status_code == 200:
                return {
                    "success": True,
                    "role": data["role"],
                    "email": data["email"],
                    "username": data["username"],
                    "message": f"Logged in as {data['role']}",
                }
            else:
                return {
                    "success": False,
                    "message": data.get("message", "Login failed"),
                }
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return {"success": False, "message": f"Login error: {e}"}


class AuthUI:
    def __init__(self, auth_service, session):
        self.auth_service = auth_service
        self.session = session

    def signup(self):
        print("\nSign Up")
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        if not self.auth_service.is_valid_email(email):
            print("Invalid email format.")
            return
        password = getpass.getpass("Password: ").strip()
        message = self.auth_service.signup(username, email, password)
        print(message)

    def login(self):
        print("\nLogin")
        email = input("Email: ").strip()
        if not self.auth_service.is_valid_email(email):
            print("Invalid email format.")
            return None
        password = getpass.getpass("Password: ").strip()
        result = self.auth_service.login(email, password)
        if result.get("success"):
            print(result.get("message"))
            self.session["email"] = result["email"]
            self.session["username"] = result["username"]
            self.session["role"] = result["role"]
            return result["role"], result["email"]
        else:
            print(result.get("message"))
            return None
