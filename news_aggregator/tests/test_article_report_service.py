import unittest
from unittest.mock import patch, MagicMock
from server.services.article_report_service import ArticleReportService


class TestArticleReportService(unittest.TestCase):
    def setUp(self):
        self.service = ArticleReportService()

    @patch("server.services.article_report_service.get_db")
    @patch("server.services.article_report_service.NotificationService")
    def test_report_article(self, mock_notification_service, mock_get_db):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.side_effect = [(1,), (1,)]
        mock_conn.cursor.return_value = mock_cursor
        mock_get_db.return_value = mock_conn

        mock_notification_instance = MagicMock()
        mock_notification_service.return_value = mock_notification_instance

        success, message = self.service.report_article("test@example.com", 1)
        self.assertTrue(success)


if __name__ == "__main__":
    unittest.main()
