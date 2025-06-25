import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    'host': os.getenv("DB_HOST", "localhost"),
    'user': os.getenv("DB_USER", "root"),
    'password': os.getenv("DB_PASSWORD", ""),
    'database': os.getenv("DB_NAME", "news_aggregator")
}

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")
THENEWSAPI_KEY = os.getenv("THENEWSAPI_KEY")
