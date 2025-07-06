import unittest
from unittest.mock import patch, MagicMock
from server.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):
    def setUp(self):
        self.service = AuthService()

    @patch("server.services.auth_service.get_db")
    @patch("server.services.auth_service.bcrypt.checkpw")
    def test_login(self, mock_checkpw, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            "id": 1, 
            "email": "test@example.com",
            "password": "hashed_password"
        }
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn
        mock_checkpw.return_value = True

        success, message, user = self.service.login("test@example.com", "password")
        self.assertTrue(success)
        self.assertEqual(user["email"], "test@example.com")

    # Add more tests for other methods...

if __name__ == "__main__":
    unittest.main()
