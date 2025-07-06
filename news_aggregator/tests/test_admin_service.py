import unittest
from unittest.mock import patch, MagicMock
from client.services.admin_service import AdminService


class TestAdminService(unittest.TestCase):
    def setUp(self):
        self.session = {"email": "admin@example.com"}
        self.service = AdminService("http://fakeapi")

    @patch("client.services.admin_service.requests.get")
    def test_get_reported_articles(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": "success", 
            "reports": [{"id": 1}]
        }
        mock_get.return_value.raise_for_status.return_value = None
        result = self.service.get_reported_articles()
        self.assertEqual(len(result), 1)

    # Add more tests for other methods...

if __name__ == "__main__":
    unittest.main()
