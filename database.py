import sqlite3
import datetime

# Define adapters and converters for date and datetime objects
def adapt_date(date):
    return date.isoformat()

def adapt_datetime(dt):
    return dt.isoformat()

def convert_date(s):
    return datetime.date.fromisoformat(s.decode('utf-8'))

def convert_datetime(s):
    return datetime.datetime.fromisoformat(s.decode('utf-8'))

# Register adapters and converters
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('date', convert_date)
sqlite3.register_converter('timestamp', convert_datetime)

def execute_query(query, parameters=(), fetchone=False):
    try:
        with sqlite3.connect("my.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES) as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            if fetchone:
                return cursor.fetchone()
            return cursor.fetchall()
    except sqlite3.Error as e:
        print(e)

def create_sqlite_tables():
    queries = [
        """CREATE TABLE IF NOT EXISTS reserveTable (
            roomNumber INTEGER,
            requestID INTEGER PRIMARY KEY,
            startDate timestamp,
            endDate timestamp,
            personQty INTEGER,
            registerationDate timestamp)""",
        """CREATE TABLE IF NOT EXISTS requestTable (
            requestID INTEGER PRIMARY KEY AUTOINCREMENT,
            startDate timestamp,
            endDate timestamp,
            personQty INTEGER,
            requestDate timestamp)""",
        """CREATE TABLE IF NOT EXISTS personTable (
            codeMelli INTEGER PRIMARY KEY,
            name TEXT,
            familyName TEXT)""",
        """CREATE TABLE IF NOT EXISTS roomTable (
            roomNumber INTEGER PRIMARY KEY,
            status TEXT)""",
        """CREATE TABLE IF NOT EXISTS request_personTable (
            requestID INTEGER,
            codeMelli INTEGER)"""
    ]
    for query in queries:
        execute_query(query)

def get_last_request_id():
    result = execute_query("SELECT requestID FROM requestTable ORDER BY requestID DESC LIMIT 1", fetchone=True)
    return result[0] if result else None
