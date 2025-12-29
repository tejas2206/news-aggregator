import getpass


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
