import MySQLdb
from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from mysql.connector import Error
import math

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key

# Database connection function
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # Change this to your database password
            database="exam_management"
        )
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/student_login', methods=['POST'])
def student_login():
    name = request.form['n']
    reg_number = request.form['rn']
    print(f"Trying to log in with Name: {name}, Registration Number: {reg_number}")

    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/')

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM student_info WHERE Name=%s AND Reg_number=%s", (name, reg_number))
        result = cursor.fetchone()

        print(f"Query Result: {result}")

        if result:
            session['rn'] = reg_number
            flash('Login Successful!', 'success')  # Flash message to be shown on student_info page
            return redirect('/student_info')  # Redirect to student_info
        else:
            flash('Invalid Info', 'danger')
            return redirect('/')

    except Error as e:
        flash(f'Error fetching data: {e}', 'danger')
        return redirect('/')

    finally:
        cursor.close()
        conn.close()

@app.route('/student_info')
def student_info():
    if 'rn' not in session:
        return redirect('/')

    reg_number = session['rn']
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/')

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT Name, Reg_number, Course, Semester FROM student_info WHERE Reg_number=%s", (reg_number,))
        student_data = cursor.fetchone()

        if student_data:
            return render_template('student_info.html', student_data=student_data)
        else:
            flash('Student information not found.', 'danger')
            return redirect('/')
    except Error as e:
        flash(f'Error fetching data: {e}', 'danger')
        return redirect('/')
    finally:
        cursor.close()
        conn.close()

@app.route('/attendance')
def attendance():
    if 'rn' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/')

    reg_number = session['rn']
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/student_info')

    attendance_records = []  # Initialize list to store attendance for each subject
    try:
        cursor = conn.cursor(dictionary=True)
        # Query to fetch attendance data for each subject for the student
        cursor.execute("SELECT subject, attended_classes, total_classes FROM attendance WHERE student_Reg_No = %s", (reg_number,))
        subjects_attendance = cursor.fetchall()

        # Process each subject's attendance data
        for record in subjects_attendance:
            attended = record['attended_classes']
            total = record['total_classes']
            subject = record['subject']
            status = 'eligible' if attended / total > 0.75 else 'fine' if attended / total > 0.5 else 'not_eligible'
            attendance_records.append({
                'subject': subject,
                'attended': attended,
                'total': total,
                'status': status
            })

        # Pass all subjects' attendance records to the template
        return render_template('attendance.html', attendance_records=attendance_records)

    except Error as e:
        flash(f'Error fetching attendance data: {e}', 'danger')
        return redirect('/student_info')
    
    finally:
        cursor.close()
        conn.close()

@app.route('/marks', methods=['GET', 'POST'])
def marks():
    if 'rn' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/')

    reg_number = session['rn']
    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/student_info')

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT subject, CIE_1, CIE_2, Event, SEE FROM marks_sheet WHERE Reg_number = %s", (reg_number,))
        marks_data = cursor.fetchall()

        cursor.execute("SELECT Name, Reg_number, Course, Semester FROM student_info WHERE Reg_number = %s", (reg_number,))
        student_data = cursor.fetchone()

        n = len(marks_data)

        if marks_data:
            total_marks = 0
            maxs_marks = n * 100
            calculated_marks = []

            for mark in marks_data:
                cie_1 = mark['CIE_1'] or 0  # Set to 0 if None
                cie_2 = mark['CIE_2'] or 0  # Set to 0 if None
                event = mark['Event'] or 0  # Set to 0 if None
                see = mark['SEE'] or 0  # Set to 0 if None

                scaled_cie_1 = math.ceil((cie_1 / 30) * 15)
                scaled_cie_2 = math.ceil((cie_2 / 30) * 15)
                scaled_event = math.ceil((event / 20) * 10)
                
                see = round((see / 100) * 60)

                subject_marks = scaled_cie_1 + scaled_cie_2 + scaled_event + see
                total_marks += subject_marks

                calculated_marks.append({
                    'subject': mark['subject'],
                    'obtained': int(subject_marks)
                })

            rounded_total_marks = round(total_marks)
            percentage = (total_marks / maxs_marks) * 100
            result = 'Pass' if percentage >= 40 else 'Fail'

            return render_template(
                'marks.html', 
                marks=calculated_marks, 
                total_marks=rounded_total_marks,  
                max_marks=maxs_marks, 
                percentage=round(percentage, 1),  
                result=result, 
                student=student_data
            )
        else:
            return render_template(
                'marks.html', 
                marks=None, 
                student=student_data,
                no_marks_message="No marks record found."
            )
    except Error as e:
        flash(f'Error fetching marks data: {e}', 'danger')
        return redirect('/student_info')
    finally:
        cursor.close()
        conn.close()

@app.route('/seat_allocation')
def seat_allocation():
    reg_number = session.get('rn')

    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/')

    cursor = conn.cursor()

    try:
        # Check for seat allocation for the student
        cursor.execute("SELECT * FROM seat_allocation WHERE Reg_number=%s", (reg_number,))
        seat_details = cursor.fetchone()

        if not seat_details:
            return render_template('seat_allocation.html', allocation_exists=False, rows=3)

        classroom_number = seat_details[1]
        seat_number = seat_details[2]

        # Retrieve the total number of seats from classroom_size
        cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no=%s", (classroom_number,))
        classroom_data = cursor.fetchone()

        if classroom_data:
            total_seats = classroom_data[0]
        else:
            flash('Classroom not found.', 'danger')
            return redirect('/')

        # Fetch all seat allocations for the specific classroom
        cursor.execute("SELECT * FROM seat_allocation WHERE Classroom_number=%s ORDER BY seat_number", (classroom_number,))
        seat_allocations = cursor.fetchall()

        # Prepare seat allocation layout with room and seat numbers
        seat_allocation = ['x'] * total_seats
        for allocation in seat_allocations:
            seat_allocation[allocation[2] - 1] = allocation[0]  # Place registration number in correct seat

        rows = 3  # Set number of rows

        return render_template(
            'seat_allocation.html', 
            allocation_exists=True, 
            reg_number=reg_number, 
            total_seats=total_seats, 
            seat_allocation=seat_allocation, 
            rows=rows, 
            seat_number=seat_number,
            classroom_number=classroom_number  # Pass the classroom number to the template
        )
    
    except Error as e:
        flash(f'Error fetching seat allocation: {e}', 'danger')
        return redirect('/')

    finally:
        cursor.close()
        conn.close()



@app.route('/exam_timetable', methods=['GET'])
def exam_timetable():
    if 'rn' not in session:
        flash('You need to log in first.', 'danger')
        return redirect('/')

    reg_number = session['rn']
    conn = get_db_connection()

    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/student_info')

    try:
        cursor = conn.cursor()
        
        # Fetch the student's course and semester
        cursor.execute("SELECT Course, Semester FROM student_info WHERE reg_number = %s", (reg_number,))
        student_course = cursor.fetchone()
        
        if student_course is None:
            flash('Student course and semester not found.', 'danger')
            return redirect('/student_info')

        # Fetch the exam timetable based on the student's course and semester
        cursor.execute("SELECT Course, Sem, Subject, Date, StartTime, EndTime FROM timetable WHERE Course = %s AND Sem = %s", 
                       (student_course[0], student_course[1]))
        results = cursor.fetchall()

        # Handle the case where no results are returned
        if not results:
            flash('No exam timetable is set for your course.', 'info')  # Message for no timetable found

        return render_template('exam_timetable.html', results=results)

    except MySQLdb.Error as e:
        flash(f'Error fetching exam timetable: {e}', 'danger')
        return redirect('/student_info')
    
    finally:
        cursor.close()
        conn.close()


@app.route('/logout')
def logout():
    # Remove the registration number from the session to log out the user
    session.pop('rn', None)
    flash('You have been logged out successfully!', 'success')
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
    