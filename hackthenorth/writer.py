from helpers import getConnection, executeReadQuery, executeWriteQuery

db = getConnection("htn.db")


query = """
CREATE TABLE IF NOT EXISTS msgs (
    msgr_id INTEGER NOT NULL,
    msg TEXT,
    sender VARCHAR(4)
);
"""
print(executeWriteQuery(db, query, ()))

# USERS
# | id | username | password |

# msgs
# | msgr_id | msg | sender |