from flask import Flask, render_template, session, redirect, flash
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="exam_management")

@app.route('/attendance')
def attendance():
    if 'rn' not in session:
        return redirect('/login')  # Ensure user is logged in

    rn = session['rn']
    con = get_db_connection()
    cursor = con.cursor()

    # Check if attendance table exists
    cursor.execute("SHOW TABLES LIKE 'attendence'")
    result = cursor.fetchone()
    if not result:
        flash('No attendance records exist')
        return redirect('/student_info')

    # Fetch attendance data
    cursor.execute("SELECT Attended_classes, Total_classes FROM attendence WHERE Reg_number = %s", (rn,))
    attendance_record = cursor.fetchone()

    if attendance_record:
        attended, total = attendance_record
        attendance = {
            'attended': attended,
            'total': total
        }

        # Determine eligibility
        if attended / total > 0.75:
            attendance['status'] = 'eligible'
            session['AE'] = 0
        elif attended / total > 0.5:
            attendance['status'] = 'fine'
            session['AE'] = 1
        else:
            attendance['status'] = 'not_eligible'
            session['AE'] = 2

        return render_template('attendance.html', attendance=attendance)

    else:
        flash('No attendance records for your register number')
        return redirect('/student_info')

if __name__ == '__main__':
    app.run(debug=True)
