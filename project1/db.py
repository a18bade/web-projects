""" database access
docs:
* http://initd.org/psycopg/docs/
* http://initd.org/psycopg/docs/pool.html
* http://initd.org/psycopg/docs/extras.html#dictionary-like-cursor
"""
import datetime

from contextlib import contextmanager
import logging
import os
from re import search
from this import d


from flask import current_app, g, redirect, session

import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None


def setup():
    global pool
    current_app.logger.info(f"creating db connection pool")
    DATABASE_URL = os.environ['DATABASE_URL']
    pool = ThreadedConnectionPool(1, 4, dsn=DATABASE_URL, sslmode='require')

    ## Temporary block for local db connect ####
    # DATABASE_URL="postgresql://danielsong:@127.0.0.1:5432/project1_db"
    # pool = ThreadedConnectionPool(1, 4, dsn=DATABASE_URL)


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
        # cursor = connection.cursor()
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

def get_login(userid, password):
    with get_db_cursor() as cur:
        # cur.execute("SELECT userid FROM login WHERE userid=%s")
        cur.execute("SELECT userid, userpassword FROM login WHERE userid=%s", [userid])
        data = cur.fetchone()
        print(data)
        if len(data) == 0:
            # User not exist
            return False
        else:
            if password == data[1]:
                return True
            else:
                # Password not matching
                return False

def add_user(nickname, email):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding user info in db")
        cur.execute("insert into user_info (nickname, email) values (%s,%s) ON CONFLICT (nickname) DO NOTHING ", (nickname, email))

def get_best_player():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM score ORDER BY score ASC limit 5")
        best_player = cur.fetchall()
        return best_player

def get_most_played():
    with get_db_cursor() as cur:
        cur.execute("SELECT username, COUNT(username) AS value_occurrence FROM score\
            GROUP BY username ORDER BY value_occurrence DESC LIMIT 1;")
        player = cur.fetchall()
        cur.execute("SELECT score, strokes FROM score WHERE username=%s", (player[0][0], ))
        data = cur.fetchall()
        score = []
        strokes = []
        for s, strok in data:
            score.append(s)
            strokes.append(strok)
        ave_score = sum(score) / len(score)
        ave_stroke = sum(strokes) / len(score)
        return player[0][0], int(ave_score), int(ave_stroke), player[0][1]


def get_score(order_asc=False, search_by=None, column=None):
    with get_db_cursor() as cur:
        if order_asc:
            if search_by != "":
                if column == 'Username':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE username like %s ORDER BY username ASC;", [search])
                elif column == 'Date':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE dateplay::text like %s ORDER BY dateplay ASC", [search])
                elif column == 'Course':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE course like %s ORDER BY course ASC", [search])
                elif column == 'Score':
                    if search_by[0] == '-' and search_by[1:].isnumeric() or search_by.isnumeric():
                        cur.execute("SELECT * FROM score WHERE score=%s::int ORDER BY score ASC", [search_by])
                elif column == 'Strokes':
                    if search_by.isnumeric():
                        cur.execute("SELECT * FROM score WHERE strokes=%s::int ORDER BY strokes ASC", [search_by])
            else:
                if column == 'Username':
                    cur.execute("SELECT * FROM score ORDER BY username ASC")
                elif column == 'Date':
                    cur.execute("SELECT * FROM score ORDER BY dateplay ASC")
                elif column == 'Course':
                    cur.execute("SELECT * FROM score ORDER BY course ASC")
                elif column == 'Score':
                        cur.execute("SELECT * FROM score ORDER BY score ASC")
                elif column == 'Strokes':
                        cur.execute("SELECT * FROM score ORDER BY strokes ASC")
        else:
            if search_by != "":
                if column == 'Username':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE username like %s ORDER BY username DESC;", [search])
                elif column == 'Date':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE dateplay::date::text like %s ORDER BY dateplay DESC", [search])
                elif column == 'Course':
                    search = "%"+search_by+"%"
                    cur.execute("SELECT * FROM score WHERE course like %s ORDER BY course DESC", [search])
                elif column == 'Score':
                    if search_by[0] == '-' and search_by[1:].isnumeric() or search_by.isnumeric():
                        cur.execute("SELECT * FROM score WHERE score=%s::int ORDER BY score DESC", [search_by])
                    else:
                        # Neeeed to be fixed!@!!!!!!!
                        cur.execute("SELECT * FROM score ORDER BY score DESC")
                elif column == 'Strokes':
                    if search_by.isnumeric():
                        cur.execute("SELECT * FROM score WHERE strokes=%s::int ORDER BY strokes DESC", [search_by])
                    else:
                        cur.execute("SELECT * FROM score ORDER BY strokes DESC")
            else:
                if column == 'Username':
                    cur.execute("SELECT * FROM score ORDER BY username DESC")
                elif column == 'Date':
                    cur.execute("SELECT * FROM score ORDER BY dateplay DESC")
                elif column == 'Course':
                    cur.execute("SELECT * FROM score ORDER BY course DESC")
                elif column == 'Score':
                    cur.execute("SELECT * FROM score ORDER BY score DESC")
                elif column == 'Strokes':
                    cur.execute("SELECT * FROM score ORDER BY strokes DESC")

        scores_raw = cur.fetchall()
        return scores_raw

def get_score_by_id(score_id):
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM score WHERE score_id=%s", [score_id])
        return cur.fetchall()

def delete_score(userid, score_id):
    with get_db_cursor(True) as cur:
        # sql = "DELETE FROM score WHERE username='{}' and score_id='{}' RETURNING (select_list | *)".format(userid, score_id)
        sql = "DELETE FROM score WHERE username='{}' and score_id='{}'".format(userid, score_id)
        cur.execute(sql)

def update_score(userid, data, score_id):
    with get_db_cursor(True) as cur:
        dateplay = data['date'] + " " + data['time']
        score = data['score']
        strokes = data['strokes']
        course = data['course']
        # sql = "update score set score='{}', strokes='{}', course='{}' where username='{}' and dateplay='{}'".format(score,strokes,course,userid,dateplay)
        sql = "UPDATE score SET score='{}', strokes='{}', course='{}', dateplay='{}' where username='{}' and score_id='{}'".format(score, strokes, course, dateplay, userid, score_id)
        cur.execute(sql)

def get_courses():
    with get_db_cursor() as cur:
        cur.execute("SELECT * FROM courses")
        return cur.fetchall()

def get_states():
    with get_db_cursor() as cur:
        cur.execute("SELECT state FROM courses")
        return cur.fetchall()

def get_user_data():
    with get_db_cursor(True) as cur:
        current_app.logger.info("Getting logged in user data")
        profile = session['profile']
        nickname = profile['nickname']
        cur.execute("select dateplay, course, score, strokes, score_id from score where username=%s", (nickname,))
        return cur.fetchall()

def add_new_score(score, strokes, course):
    with get_db_cursor(True) as cur:
        # INSERT INTO score (username, dateplay, course, score, strokes) Values ('song0254', TO_DATE('01/12/2022', 'MM/DD/YYYY'), 'RiverFront', -4, 50);
        #cur.execute("DELETE FROM score WHERE username = 'google-oauth2|107702518420736406929';")
        current_app.logger.info("Adding new score")
        profile = session['profile']
        user_id = profile['nickname']  
        cur.execute("INSERT INTO score (username, dateplay, course, score, strokes) Values (%s, %s, %s, %s, %s)", (user_id, datetime.datetime.now().isoformat(timespec='seconds'), course, score, strokes))
        

# def date_specific_user_data(date_result):
#     with get_db_cursor(True) as cur:
#         current_app.logger.info("Getting logged in user data for specified date")
#         profile = session['profile']
#         user_id = profile['user_id']
#         cur.execute("select to_char(dateplay, ('YYYY-MM-DD')) as day, course, score, strokes from score where username=%s and dateplay=%s", (user_id, date_result))
#         return cur.fetchall()

# def course_specific_user_data(course):
#     with get_db_cursor(True) as cur:
#         current_app.logger.info("Getting logged in user data for specified course")
#         profile = session['profile']
#         user_id = profile['user_id']
#         cur.execute("select to_char(dateplay, ('YYYY-MM-DD')) as day, course, score, strokes from score where username=%s and course=%s", (user_id, course))
#         return cur.fetchall()


def personal_progress_search(course, dates):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Getting logged in user data for specified course and date")
        profile = session['profile']
        user_id = profile['nickname']

        if dates is None:
            cur.execute("select to_char(dateplay, ('YYYY-MM-DD')), course, score, strokes, score_id from score where username=%s and course=%s", (user_id, course))
        elif (course == 'All' and dates is not None):
            cur.execute("select to_char(dateplay, ('YYYY-MM-DD')), course, score, strokes, score_id from score where username=%s and dateplay::date=%s", (user_id, dates))
        else:
            cur.execute("select to_char(dateplay, ('YYYY-MM-DD')), course, score, strokes, score_id from score where username=%s and course=%s and dateplay::date=%s", (user_id, course, dates))
        
        data = cur.fetchall()
        return data

    
def get_scores():
    results = get_user_data()
    scores = []
    for result in results:
        scores.append(result[2])
    return scores

def get_dates():
    results = get_user_data()
    dates = []
    for result in results:
        data = str(result[0]) 
        dates.append(data)
    return dates

def get_strokes():
    results = get_user_data()
    strokes = []
    for result in results:
        strokes.append(result[3])
    return strokes

