import logging
import bcrypt
import re
from server.db.database import get_db


class AuthService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

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
            return False, validation_message

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "User already exists"
            hashed = bcrypt.hashpw(
                password.encode(), bcrypt.gensalt()
            ).decode()
            cursor.execute(
                """INSERT INTO users (username, email, password, role)
                   VALUES (%s, %s, %s, %s)""",
                (username, email, hashed, "user"),
            )
            conn.commit()
            cursor.close()
            return True, "User registered successfully"
        except Exception as e:
            self.logger.error(f"Error during signup: {e}")
            return False, "Signup failed"

    def login(self, email, password):
        try:
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            if not user or not bcrypt.checkpw(
                password.encode(), user["password"].encode()
            ):
                return False, "Invalid credentials", None
            return True, "Login successful", user
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False, "Login failed", None
