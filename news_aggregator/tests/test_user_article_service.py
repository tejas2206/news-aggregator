import unittest
from unittest.mock import patch, MagicMock
from server.services.user_article_service import UserArticleService


class TestUserArticleService(unittest.TestCase):
    def setUp(self):
        self.service = UserArticleService()

    @patch("server.services.user_article_service.get_db")
    def test_get_headlines_by_range(self, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        # Mock blocked keywords query first, then articles query
        mock_cursor.fetchall.side_effect = [
            [],  # blocked keywords (empty)
            [{"id": 1, "title": "Test"}]  # articles
        ]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        result = self.service.get_headlines_by_range("2025-01-01", "2025-01-02")
        self.assertEqual(result, [{"id": 1, "title": "Test"}])

    # Add more tests for other methods...

if __name__ == "__main__":
    unittest.main()
