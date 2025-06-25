import re
import requests
import getpass


class AuthHandler:
    def __init__(self, session, base_url):
        self.session = session
        self.base_url = base_url

    def is_valid_email(self, email):
        pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        return re.match(pattern, email)

    def signup(self):
        print("\nSign Up")
        username = input("Username: ").strip()
        email = input("Email: ").strip()

        if not self.is_valid_email(email):
            print("Invalid email format.")
            return

        password = getpass.getpass("Password: ").strip()

        try:
            response = requests.post(
                f"{self.base_url}/auth/signup",
                json={"username": username, "email": email, "password": password},
            )
            print(response.json().get("message"))
        except Exception as e:
            print("Signup error:", str(e))

    def login(self):
        print("\nLogin")
        email = input("Email: ").strip()

        if not self.is_valid_email(email):
            print("Invalid email format.")
            return None

        password = getpass.getpass("Password: ").strip()

        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"email": email, "password": password},
            )
            data = response.json()

            if response.status_code == 200:
                print(f"Logged in as {data['role']}")
                self.session["email"] = data["email"]
                self.session["username"] = data["username"]
                self.session["role"] = data["role"]
                return data["role"], data["email"]
            else:
                print(f"{data.get('message', 'Login failed')}")
                return None
        except Exception as e:
            print("Login error:", str(e))
            return None
