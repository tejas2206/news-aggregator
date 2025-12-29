import logging
import bcrypt
import re
from server.db.database import get_db


class AuthService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def is_valid_username(self, username):
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"

        if len(username) > 20:
            return False, "Username must be less than 20 characters long"

        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return False, "Username can only contain letters, numbers, and underscores"

        if username[0].isdigit():
            return False, "Username cannot start with a number"

        return True, "Username is valid"

    def is_username_unique(self, username):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()

            if result:
                return False, "Username is already taken"
            return True, "Username is available"

        except Exception as e:
            self.logger.error(f"Error checking username uniqueness: {e}")
            return False, f"Database error: Unable to check username availability"

        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

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
        is_valid_user, username_message = self.is_valid_username(username)
        if not is_valid_user:
            return False, username_message

        is_unique_user, uniqueness_message = self.is_username_unique(username)
        if not is_unique_user:
            return False, uniqueness_message

        is_valid, validation_message = self.is_valid_password(password)
        if not is_valid:
            return False, validation_message

        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                cursor.close()
                return False, "User already exists"

            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
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
