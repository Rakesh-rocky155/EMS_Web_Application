import mysql.connector
from mysql.connector import Error

def drop_attendance_table():
    con = None  # Initialize con to None
    try:
        # Establish a database connection
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='exam_management'
        )

        if con.is_connected():
            cursor = con.cursor()

            # Check if the attendance table exists
            cursor.execute("SHOW TABLES LIKE 'attendance'")
            result = cursor.fetchone()

            if result:
                # Drop the attendance table if it exists
                cursor.execute("DROP TABLE attendance")
                con.commit()
                print("All attendance records are cleared")
            else:
                print("No records exist to clear")
        
    except Error as e:
        print(f"Error: {e}")
    finally:
        if con is not None and con.is_connected():  # Ensure con is not None
            cursor.close()
            con.close()
            print("Database connection closed.")

if __name__ == "__main__":
    drop_attendance_table()
