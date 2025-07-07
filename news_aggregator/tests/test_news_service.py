import unittest
from unittest.mock import patch
from client.services.news_service import NewsService


class TestNewsService(unittest.TestCase):
    def setUp(self):
        self.session = {"email": "test@example.com"}
        self.service = NewsService("http://fakeapi", self.session)

    @patch("client.services.news_service.requests.get")
    def test_fetch_categories_success(self, mock_get):
        mock_get.return_value.json.return_value = {
            "status": "success",
            "categories": ["tech"],
        }
        self.assertIn("tech", self.service.fetch_categories())

    @patch("client.services.news_service.requests.get")
    def test_get_today_headlines(self, mock_get):
        mock_get.return_value.json.return_value = {"articles": [{"id": 1}]}
        self.assertEqual(len(self.service.get_today_headlines("all")), 1)

    @patch("client.services.news_service.requests.post")
    def test_save_article(self, mock_post):
        mock_post.return_value.json.return_value = {"message": "Saved"}
        self.assertEqual(self.service.save_article(1), "Saved")


if __name__ == "__main__":
    unittest.main()
