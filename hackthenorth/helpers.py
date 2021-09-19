from flask import redirect, session, render_template
from functools import wraps
import sqlite3


# decorates routes to require login
def login_required(f):
    # http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/"
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/signin")
        return f(*args, **kwargs)
    return decorated_function


# connect database with sqlite3
def getConnection(db):
    connection = sqlite3.connect(db, check_same_thread=False)
    return connection


# execute a write query into database
def executeWriteQuery(connection, query, placeholders):
    cursor = connection.cursor()
    print(query, placeholders)
    cursor.execute(query, placeholders)
    connection.commit()
    return True


# execute a read query from database
def executeReadQuery(connection, query, placeholders):
    cursor = connection.cursor()
    print(query, placeholders)
    cursor.execute(query, placeholders)
    return cursor.fetchall()


def getusermsgs(db, placeholders):
    query = "SELECT msg, sender FROM msgs WHERE msgr_id = ?"
    raw_outputs = executeReadQuery(db, query, placeholders)
    return raw_outputs


# we have to apologize for errors
def apology(message, code):
    #Escape special characters: https://github.com/jacebrowning/memegen#special-characters
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"), ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("error.html", top=code, bottom=escape(message)), code