import unittest
from unittest.mock import patch, MagicMock
from client.services.auth_handler import AuthService

class TestAuthHandler(unittest.TestCase):
    def setUp(self):
        self.service = AuthService("http://fakeapi")

    @patch("client.services.auth_handler.requests.post")
    def test_signup(self, mock_post):
        mock_post.return_value.json.return_value = {"message": "Signup successful"}
        mock_post.return_value.raise_for_status.return_value = None
        result = self.service.signup("user", "test@example.com", "pass")
        self.assertEqual(result, "Signup successful")

    # Add more tests for other methods...

if __name__ == "__main__":
    unittest.main()
