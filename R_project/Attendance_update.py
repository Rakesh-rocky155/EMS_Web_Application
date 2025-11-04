from flask import Flask, session, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set your secret key for session management

def db_connection():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="exam_management"
        )
        return con
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/attendence_update')
def attendence_update():
    # Retrieve session data
    rn = session.get('rn')
    ac = session.get('ac')
    tc = session.get('tc')

    if not rn or not ac or not tc:
        return "<script>alert('Session data missing!'); window.location.replace('/attendence_set_form');</script>"

    con = db_connection()
    
    if con:
        cursor = con.cursor()

        # Update attendance record
        update_query = "UPDATE attendance SET Attended_classes = %s, Total_Classes = %s WHERE Reg_number = %s"
        cursor.execute(update_query, (ac, tc, rn))
        con.commit()

        if cursor.rowcount > 0:
            return "<script>alert('Attendance Updated'); window.location.replace('/attendence_set_form');</script>"
        else:
            return "<script>alert('Update failed!'); window.location.replace('/attendence_set_form');</script>"
    
    else:
        return "<script>alert('Database connection failed!'); window.location.replace('/attendence_set_form');</script>"

if __name__ == "__main__":
    app.run(debug=True)
