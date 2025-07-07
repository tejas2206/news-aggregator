import unittest
from unittest.mock import patch
from client.services.notification_service import NotificationService


class TestNotificationService(unittest.TestCase):
    def setUp(self):
        self.session = {"email": "test@example.com"}
        self.service = NotificationService("http://fakeapi")

    @patch("client.services.notification_service.requests.get")
    def test_get_notification_settings(self, mock_get):
        mock_get.return_value.json.return_value = {
            "categories": [{"id": 1}],
            "keywords": ["test"],
        }
        mock_get.return_value.raise_for_status.return_value = None
        result = self.service.get_notification_settings("test@example.com")
        self.assertEqual(len(result["categories"]), 1)


if __name__ == "__main__":
    unittest.main()
