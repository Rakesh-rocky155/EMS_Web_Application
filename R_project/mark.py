from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Database connection setup
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',  # your password
        database='attendance_db'  # your database
    )

# Route for setting attendance
@app.route('/set_attendance', methods=['GET', 'POST'])
def set_attendance():
    if request.method == 'POST':
        student_name = request.form['student_name']
        attended_classes = request.form['attended_classes']
        total_classes = request.form['total_classes']

        conn = get_db_connection()
        cursor = conn.cursor()

        # Insert data into the attendance table
        sql = 'INSERT INTO attendance (student_name, attended_classes, total_classes) VALUES (%s, %s, %s)'
        cursor.execute(sql, (student_name, attended_classes, total_classes))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('view_attendance'))
    return render_template('set_attendance.html')

# Route for viewing attendance
@app.route('/view_attendance')
def view_attendance():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch attendance records
    cursor.execute('SELECT student_name, attended_classes, total_classes FROM attendance')
    attendance_records = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('view_attendance.html', attendance_records=attendance_records)

# Route for clearing attendance records
@app.route('/clear_records')
def clear_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Clear the attendance table
    cursor.execute('DELETE FROM attendance')
    conn.commit()

    cursor.close()
    conn.close()

    return redirect(url_for('view_attendance'))

if __name__ == '__main__':
    app.run(debug=True)
