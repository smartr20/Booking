import sqlite3
import datetime
import jdatetime
from persiantools.jdatetime import JalaliDate
from tabulate import tabulate


# Define the current date and time
current_date = datetime.date.today()
current_date_time = datetime.datetime.now()


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


def get_user_jalali_date_input(which_date):
    while True:
        user_input = input(f"Enter a Persian date for {which_date} (YYYY-MM-DD): ")
        try:
            # Parse the input string to a JalaliDate object
            jalali_date = JalaliDate.fromisoformat(user_input)
            # Convert JalaliDate to Gregorian date
            return jalali_date.to_gregorian()
        except ValueError:
            # Handle invalid date formats
            print("Invalid date format. Please enter the Persian date in YYYY-MM-DD format.")


def execute_query(query, parameters=(), fetchone=False):
    """Execute a query and handle errors."""
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
    """Create tables in an SQLite database."""
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


def insert_data(table, columns, values):
    """Insert data into a table."""
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(values))})"
    execute_query(query, values)
    print("Registered")


def display_table(table):
    """Display the contents of a table."""
    query = f"SELECT * FROM {table}"
    query_list_map = {
        'reserveTable': [2, 3, 5],
        'requestTable': [1, 2, 4]
    }

    rows = execute_query(query)
    if rows:
        column_names = [desc[0] for desc in execute_query(f"PRAGMA table_info({table})")]
        converted_rows = []
        for row in rows:
            converted_row = list(row)
            for i in query_list_map.get(table, []):  # Convert dates based on table
                if isinstance(row[i], datetime.date):
                    gregorian_date = row[i]
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    converted_row[i] = jalali_date.isoformat()
            converted_rows.append(converted_row)
        print(tabulate(converted_rows, headers=column_names, tablefmt="grid"))
    else:
        print(f"No data found in {table}.")


def get_last_request_id():
    """Get the last requestID from requestTable."""
    result = execute_query("SELECT requestID FROM requestTable ORDER BY requestID DESC LIMIT 1", fetchone=True)
    return result[0] if result else None


def check_codeMelli_in_personTable(codeMelli):
    """Check if a codeMelli exists in the personTable."""
    result = execute_query("SELECT 1 FROM personTable WHERE codeMelli = ?", (codeMelli,), fetchone=True)
    found = result is not None
    print(f"{'Person with codeMelli {codeMelli} found' if found else 'No person found'} in personTable.")
    return found


def check_reservations_in_date_range(start_date, end_date):
    """Check if there are reservations in the given date range."""
    query = """SELECT * FROM reserveTable WHERE startDate <= ? AND endDate >= ?"""
    rows = execute_query(query, (end_date, start_date))
    if rows:
        print("Reservations found in the given date range:")
        display_table('reserveTable')
    else:
        print("No reservations found in the given date range.")


def register_person(last_request_id, person_qty):
    """Register persons associated with a request."""
    for _ in range(person_qty):
        name = input("What is your name? ")
        familyName = input("What is your family name? ")
        codeMelli = int(input("What is your melli code? "))

        if not check_codeMelli_in_personTable(codeMelli):
            insert_data('personTable', ['codeMelli', 'name', 'familyName'], [codeMelli, name, familyName])
        insert_data('request_personTable', ['requestID', 'codeMelli'], [last_request_id, codeMelli])


def registeration(room_number, person_qty, start_date, end_date):
    """Register a new reservation."""
    last_request_id = get_last_request_id()
    insert_data('reserveTable', ['roomNumber', 'requestID', 'startDate', 'endDate', 'personQty', 'registerationDate'],
                [room_number, last_request_id, start_date, end_date, person_qty, current_date])
    register_person(last_request_id, person_qty)


def get_empty_rooms_in_date_range(start_date, end_date):
    """Check which rooms from 201 to 217 are empty in the given date range."""
    total_rooms = set(range(201, 218))
    occupied_rooms_query = """
    SELECT roomNumber FROM reserveTable WHERE NOT (endDate < ? OR startDate > ?)
    """
    occupied_rooms = {room[0] for room in execute_query(occupied_rooms_query, (start_date, end_date))}

    empty_rooms = total_rooms - occupied_rooms
    if empty_rooms:
        print(f"The following rooms are empty from {start_date} to {end_date}:")
        print(", ".join(map(str, sorted(empty_rooms))))

        if input("Do you want to register it? (y/n): ").lower() == "y":
            add_request(start_date, end_date)
    else:
        print("No rooms are empty in the given date range.")


def add_request(start_date, end_date):
    """Add a new request."""
    person_qty = int(input("How many persons: "))
    room_number = int(input("What is Room Number: "))
    insert_data('requestTable', ['startDate', 'endDate', 'personQty', 'requestDate'],
                [start_date, end_date, person_qty, current_date_time])
    registeration(room_number, person_qty, start_date, end_date)
    display_table('reserveTable')


if __name__ == '__main__':
    create_sqlite_tables()
    user_input = input("How can I help you: 1. Show reserveTable 2. Show requestTable 3. Add request: ")
    if user_input == "1":
        display_table('reserveTable')
    elif user_input == "2":
        display_table('requestTable')
    elif user_input == "3":
        start_date = get_user_jalali_date_input("start Date")
        end_date = get_user_jalali_date_input("end Date")
        get_empty_rooms_in_date_range(start_date, end_date)
