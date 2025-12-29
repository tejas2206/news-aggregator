import unittest
from unittest.mock import patch
from client.services.auth_handler import AuthService


class TestAuthHandler(unittest.TestCase):
    def setUp(self):
        self.service = AuthService("http://fakeapi")

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

    def test_password_validation_various_special_chars(self):
        test_passwords = [
            "Password1@",
            "Password1#",
            "Password1$",
            "Password1%",
            "Password1^",
            "Password1&",
            "Password1*",
        ]
        for password in test_passwords:
            is_valid, message = self.service.is_valid_password(password)
            self.assertTrue(is_valid, f"Password {password} should be valid")

    @patch("client.services.auth_handler.requests.post")
    def test_signup_with_invalid_password(self, mock_post):
        result = self.service.signup("user", "test@example.com", "weak")
        self.assertEqual(result, "Password must be at least 6 characters long")
        mock_post.assert_not_called()

    @patch("client.services.auth_handler.requests.post")
    def test_signup_with_valid_password(self, mock_post):
        mock_post.return_value.json.return_value = {"message": "Signup successful"}
        mock_post.return_value.raise_for_status.return_value = None
        result = self.service.signup("user", "test@example.com", "Password1!")
        self.assertEqual(result, "Signup successful")
        mock_post.assert_called_once()

    @patch("client.services.auth_handler.requests.post")
    def test_signup(self, mock_post):
        mock_post.return_value.json.return_value = {"message": "Signup successful"}
        mock_post.return_value.raise_for_status.return_value = None
        result = self.service.signup("user", "test@example.com", "Password1!")
        self.assertEqual(result, "Signup successful")


if __name__ == "__main__":
    unittest.main()
