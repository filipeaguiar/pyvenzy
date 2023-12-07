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
    """
    Classe responsável por lidar com o banco de dados.
    """

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
        """
        Obtém a data e hora atual do banco de dados.

        Returns:
            str: A data e hora atual do banco de dados.
        """
        conn = DataBase.pool.getconn()
        cursor = conn.cursor()
        cursor.execute("SELECT to_char(now(), 'YYYY-MM-DD HH24:MI:SS.US')")
        result = cursor.fetchone()[0]
        DataBase.pool.putconn(conn)
        return result

    @staticmethod
    def formatedquery(query: str, date: tuple) -> str:
        """
        Formata uma query SQL.

        Args:
            query (str): A query SQL.
            date (tuple): A data e hora.
            
        Returns:
            str: A query SQL formatada.
        """
        return str.format(query, date)

    @staticmethod
    def readSQL(file_name):
        """
        Lê um arquivo SQL.
        
        Args:
            file_name (str): O nome do arquivo SQL.

        Returns:
            str: O conteúdo do arquivo SQL.
        """
        with open(os.path.join(sys.path[0], f"sql/{file_name}.sql"), "r") as file:
            content = file.read()
        return content

    @staticmethod
    def runQuery(query):
        """
        Executa uma query SQL.

        Args:
            query (str): A query SQL.

        Returns:
            list: O resultado da query SQL.
        """
        conn = DataBase.pool.getconn()
        cursor = conn.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(query)
        result = cursor.fetchall()
        DataBase.pool.putconn(conn)
        return result
