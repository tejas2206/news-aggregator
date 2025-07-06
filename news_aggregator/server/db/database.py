import mysql.connector
import logging
from config import DB_CONFIG

connection = None
logger = logging.getLogger(__name__)


def init_db():
    global connection
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            auth_plugin="mysql_native_password",
        )
        logger.info("Database connected.")
    except mysql.connector.Error as err:
        logger.error(f"DB connection failed: {err}")
        connection = None


def get_db():
    global connection
    if connection is None or not connection.is_connected():
        init_db()
    if connection is None:
        logger.critical("DB connection not established.")
        raise ConnectionError("DB connection not established.")
    return connection
