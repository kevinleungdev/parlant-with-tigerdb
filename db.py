from contextlib import contextmanager
import psycopg2

from env import TIMESCALE_DATABASE_URL, TIMESCALE_DATABASE_PASSWORD


def get_connection():
    conn = psycopg2.connect(TIMESCALE_DATABASE_URL, password=TIMESCALE_DATABASE_PASSWORD)
    try:
        yield conn
    finally:
        conn.close()


get_db = contextmanager(get_connection)