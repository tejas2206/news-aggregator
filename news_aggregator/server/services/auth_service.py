import logging
import bcrypt
from server.db.database import get_db


class AuthService:
    def __init__(self, logger=None):
        self.logger = logger or logging.getLogger(__name__)

    def signup(self, username, email, password):
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return False, "User already exists"
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            cursor.execute(
                "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
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
