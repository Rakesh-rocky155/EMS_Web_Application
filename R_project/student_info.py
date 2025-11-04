from flask import Flask, render_template, session
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session management

# Database connection
def get_db_connection():
    return MySQLdb.connect(host='localhost', user='root', passwd='', db='exam_management')

@app.route('/student_dashboard')
def student_dashboard():
    rn = session.get('rn')  # Getting the registration number from session

    if not rn:
        return "Session expired or invalid", 400

    # Connect to the database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch student information
    cursor.execute("SELECT * FROM student_info WHERE Reg_number=%s", (rn,))
    student_info = cursor.fetchone()

    conn.close()

    if student_info:
        student_data = {
            'name': student_info[1],
            'reg_number': student_info[0],
            'course': student_info[2],
            'semester': student_info[3],
        }
        return render_template('student_dashboard.html', student_data=student_data)
    else:
        return "No student information found", 404

if __name__ == '__main__':
    app.run(debug=True)
