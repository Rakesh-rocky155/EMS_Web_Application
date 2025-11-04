import mysql.connector
from mysql.connector import Error

try:
    # Establishing the connection to the MySQL database
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="exam_management"
    )
    
    if con.is_connected():
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        verify = False
        for table in tables:
            if table[0] == "attendance":
                verify = True

        if verify:
            cursor.execute("DROP TABLE attendance")
            con.commit()
            print('All attendance records are cleared')
            # Redirect to HTML page (this can be handled in a Flask web app)
            print('Redirecting to A Attendence Set.html')
        else:
            print('No records exist to clear')
            print('Redirecting to A Attendence Set.html')

except Error as e:
    print(f"Error: {e}")
    print('Please check database connection')
    # Redirect to HTML page (this can be handled in a Flask web app)
    print('Redirecting to A Attendence Set.html')

finally:
    if con.is_connected():
        cursor.close()
        con.close()
