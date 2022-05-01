from contextlib import contextmanager
import logging
import os
from flask import current_app, g

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None
def setup():
    global pool
    DATABASE_URL = os.environ['DATABASE_URL']
    current_app.logger.info(f"creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=DATABASE_URL, sslmode='require')


@contextmanager
def get_db_connection():
    try:
        connection = pool.getconn()
        yield connection
    finally:
        pool.putconn(connection)


@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as connection:
      cursor = connection.cursor(cursor_factory=DictCursor)
      try:
          yield cursor
          if commit:
              connection.commit()
      finally:
          cursor.close()

def add_response(favorite_movie,favorite_movie_genre,aspect,watched_uncharted,favorite_info_about_uncharted):
    with get_db_cursor(True) as cur:
        cur.execute("INSERT into data_entries (favorite_movie,favorite_movie_genre,aspect,watched_uncharted,favorite_info_about_uncharted,time) values (%s,%s,%s,%s,%s,current_timestamp)", (favorite_movie,favorite_movie_genre,aspect,watched_uncharted,favorite_info_about_uncharted))


def api_results(isReversed):
    results = []
    with get_db_cursor(True) as cur:
        if isReversed:
            cur.execute("select * from data_entries order by time;")
        else:
            cur.execute("select * from data_entries order by time desc;")
        rows = cur.fetchall()
        i = 0
        for row in rows:
            results.append(row)
    return results
