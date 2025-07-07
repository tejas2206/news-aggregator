import unittest
from unittest.mock import patch, MagicMock
from server.services.user_notification_service import UserNotificationService


class TestUserNotificationService(unittest.TestCase):
    def setUp(self):
        self.service = UserNotificationService()

    @patch("server.services.user_notification_service.get_db")
    def test_get_notifications(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {"id": 1}
        mock_cursor.fetchall.side_effect = [
            [{"category": "tech", "enabled": True}],
            [{"keyword": "test"}],
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        success, message, categories, keywords = self.service.get_notifications(
            "test@example.com"
        )
        self.assertTrue(success)
        self.assertEqual(len(categories), 1)
        self.assertEqual(keywords, ["test"])


if __name__ == "__main__":
    unittest.main()
