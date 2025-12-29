import unittest
from unittest.mock import patch, MagicMock
from server.services.user_feedback_service import UserFeedbackService


class TestUserFeedbackService(unittest.TestCase):
    def setUp(self):
        self.service = UserFeedbackService()

    @patch("server.services.user_feedback_service.get_db")
    def test_like_article(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1,)
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        success, message = self.service.like_article("test@example.com", 1)
        self.assertTrue(success)
        self.assertEqual(message, "You liked this article.")


if __name__ == "__main__":
    unittest.main()
