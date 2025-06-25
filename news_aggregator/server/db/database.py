import mysql.connector
from config import DB_CONFIG

connection = None


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
        print("Database connected.")
    except mysql.connector.Error as err:
        print(f"DB connection failed: {err}")
        connection = None


def get_db():
    global connection
    if connection is None or not connection.is_connected():
        init_db()
    if connection is None:
        raise ConnectionError("DB connection not established.")
    return connection
