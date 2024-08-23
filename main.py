from database import create_sqlite_tables, get_last_request_id, execute_query
from reservation import add_request, display_table, get_empty_rooms_in_date_range, get_user_jalali_date_input

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
