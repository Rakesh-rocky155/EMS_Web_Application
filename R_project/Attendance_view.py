from flask import Flask, render_template_string
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

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

@app.route('/student_attendance')
def student_attendance():
    con = db_connection()
    
    if con:
        cursor = con.cursor()

        # Check if the attendance table exists
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        verify = False
        for table in tables:
            if table[0] == "attendance":
                verify = True

        if not verify:
            # No attendance records found
            return "<script>alert('No attendance records exist'); window.location.replace('/info');</script>"

        # Query for attendance records
        cursor.execute("SELECT * FROM attendance ORDER BY Reg_number")
        attendance_records = cursor.fetchall()

        student_data = []
        for record in attendance_records:
            reg_number = record[0]
            attended_classes = record[1]
            total_classes = record[2]

            # Query for student name based on registration number
            cursor.execute("SELECT Name FROM Student_info WHERE Reg_number = %s", (reg_number,))
            student_name = cursor.fetchone()

            if student_name:
                student_data.append((student_name[0], attended_classes, total_classes))
            else:
                student_data.append(("Student not registered", attended_classes, total_classes))

        # Render the HTML table with attendance data
        return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Student Attendance Display</title>
            <style>
                body {
                    background-image: url('/static/images/Classroom2.jpg');
                    background-repeat: no-repeat;
                    background-size: cover;
                    text-align:center;
                }
                table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                    border: 0.5px solid black;
                }
                th, td {
                    background-color: #111;
                    opacity: 0.8;
                    color: #fff;
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                    border: 0.5px solid black;
                }
            </style>
        </head>
        <body>
            <h1>Student Attendance</h1>
            <div>
                <table>
                    <tr>
                        <th>Student Name</th>
                        <th>Attended Classes</th>
                        <th>Total Classes</th>
                    </tr>
                    {% for student in student_data %}
                    <tr>
                        <td>{{ student[0] }}</td>
                        <td>{{ student[1] }}</td>
                        <td>{{ student[2] }}</td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
        </html>
        """, student_data=student_data)
    
    else:
        return "<script>alert('Database connection failed');</script>"

if __name__ == "__main__":
    app.run(debug=True)
