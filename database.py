from dotenv import load_dotenv
from psycopg2 import pool, extras
import os
import sys

load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_DB = os.getenv("PG_DB")
PG_HOST = os.getenv("PG_HOST")
PG_PORT = os.getenv("PG_PORT")


class DataBase:
    pool = pool.SimpleConnectionPool(
        1,
        20,
        user=PG_USER,
        password=PG_PASSWORD,
        host=PG_HOST,
        port=PG_PORT,
        database=PG_DB,
    )

    @staticmethod
    def getTime():
        conn = DataBase.pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS.US')")
        result = cursor.fetchone()[0]
        DataBase.pool.putconn(conn)
        return result

    @staticmethod
    def formatedquery(query: str, date: tuple) -> str:
        return str.format(query, date)

    @staticmethod
    def readSQL(file_name):
        with open(os.path.join(sys.path[0], f"sql/{file_name}.sql"), "r") as file:
            content = file.read()
        return content

    @staticmethod
    def runQuery(query):
        conn = DataBase.pool.getconn()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(query)
        result = cursor.fetchall()
        DataBase.pool.putconn(conn)
        return result
