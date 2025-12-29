import unittest
from unittest.mock import patch, MagicMock
from server.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.service = AuthService()

    def test_password_validation_too_short(self):
        is_valid, message = self.service.is_valid_password("12345")
        self.assertFalse(is_valid)
        self.assertEqual(message, "Password must be at least 6 characters long")

    def test_password_validation_no_capital(self):
        is_valid, message = self.service.is_valid_password("password1!")
        self.assertFalse(is_valid)
        self.assertEqual(message, "Password must contain at least one capital letter")

    def test_password_validation_no_digit(self):
        is_valid, message = self.service.is_valid_password("Password!")
        self.assertFalse(is_valid)
        self.assertEqual(message, "Password must contain at least one digit")

    def test_password_validation_no_special_char(self):
        is_valid, message = self.service.is_valid_password("Password1")
        self.assertFalse(is_valid)
        self.assertEqual(message, "Password must contain special character")

    def test_password_validation_valid(self):
        is_valid, message = self.service.is_valid_password("Password1!")
        self.assertTrue(is_valid)
        self.assertEqual(message, "Password is valid")

    @patch("server.services.auth_service.get_db")
    def test_signup_with_invalid_password(self, mock_get_db):
        success, message = self.service.signup("user", "test@example.com", "weak")
        self.assertFalse(success)
        self.assertEqual(message, "Password must be at least 6 characters long")
        mock_get_db.assert_not_called()

    @patch("server.services.auth_service.get_db")
    @patch("server.services.auth_service.bcrypt.hashpw")
    def test_signup_with_valid_password(self, mock_hashpw, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        mock_hashpw.return_value.decode.return_value = "hashed_password"

        success, message = self.service.signup("user", "test@example.com", "Password1!")
        self.assertTrue(success)
        self.assertEqual(message, "User registered successfully")
        mock_get_db.assert_called_once()

    @patch("server.services.auth_service.get_db")
    @patch("server.services.auth_service.bcrypt.checkpw")
    def test_login(self, mock_checkpw, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 1,
            "email": "test@example.com",
            "password": "hashed_password",
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        mock_checkpw.return_value = True

        success, message, user = self.service.login("test@example.com", "password")
        self.assertTrue(success)
        self.assertEqual(user["email"], "test@example.com")


if __name__ == "__main__":
    unittest.main()
