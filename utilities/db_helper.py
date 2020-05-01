import psycopg2

from config import Config


def execute_sql_query(sql_query):
    conn = psycopg2.connect(f"dbname='{Config.DB_NAME}' user='{Config.DB_USERNAME}' host='{Config.DB_HOST}' "
                            f"password='{Config.DB_PASSWORD}' port='{Config.DB_PORT}'{Config.DB_USESSL}")
    cursor = conn.cursor()
    cursor.execute(sql_query)
    return cursor.fetchall()
