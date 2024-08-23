import datetime
import jdatetime
from persiantools.jdatetime import JalaliDate
from tabulate import tabulate
from database import execute_query, get_last_request_id

current_date = datetime.date.today()
current_date_time = datetime.datetime.now()

def get_user_jalali_date_input(which_date):
    while True:
        user_input = input(f"Enter a Persian date for {which_date} (YYYY-MM-DD): ")
        try:
            jalali_date = JalaliDate.fromisoformat(user_input)
            return jalali_date.to_gregorian()
        except ValueError:
            print("Invalid date format. Please enter the Persian date in YYYY-MM-DD format.")

def insert_data(table, columns, values):
    query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(['?'] * len(values))})"
    execute_query(query, values)
    #print("Registered")

def display_table(table):
    query_list_map = {
        'reserveTable': [2, 3, 5],
        'requestTable': [1, 2, 4]
    }

    rows = execute_query(f"SELECT * FROM {table}")
    if rows:
        column_names = [desc[0] for desc in execute_query(f"PRAGMA table_info({table})")]
        converted_rows = []
        for row in rows:
            converted_row = list(row)
            for i in query_list_map.get(table, []):
                if isinstance(row[i], datetime.date):
                    gregorian_date = row[i]
                    jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
                    converted_row[i] = jalali_date.isoformat()
            converted_rows.append(converted_row)
        print(tabulate(converted_rows, headers=column_names, tablefmt="grid"))
    else:
        print(f"No data found in {table}.")


def check_codeMelli_in_personTable(codeMelli):
    """Check if a codeMelli exists in the personTable."""
    query = "SELECT * FROM personTable WHERE codeMelli = ?"
    result = execute_query(query, (codeMelli,), fetchone=True)
    if result:
        print(f"Person with codeMelli {codeMelli} found in personTable.")
        return True
    else:
        print(f"No person found with codeMelli {codeMelli} in personTable.")
        return False

def registeration(room_number, person_qty, start_date, end_date):
    last_request_id = get_last_request_id()
    insert_data('reserveTable', ['roomNumber', 'requestID', 'startDate', 'EndDate', 'personQty', 'registerationDate'],
                [room_number, last_request_id, start_date, end_date, person_qty, current_date])
    for _ in range(person_qty):
        name = input("What is your name? ")
        familyName = input("What is your family name? ")
        codeMelli = int(input("What is your melli code? "))
        if not check_codeMelli_in_personTable(codeMelli):
            insert_data('personTable', ['codeMelli', 'name', 'familyName'], [codeMelli, name, familyName])
        insert_data('request_personTable', ['requestID', 'codeMelli'], [last_request_id, codeMelli])

def get_empty_rooms_in_date_range(start_date, end_date):
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
    person_qty = int(input("How many persons: "))
    room_number = int(input("What is Room Number: "))
    insert_data('requestTable', ['startDate', 'endDate', 'personQty', 'requestDate'],
                [start_date, end_date, person_qty, current_date_time])
    registeration(room_number, person_qty, start_date, end_date)
    display_table('reserveTable')
