from flask import Flask, render_template, request, redirect, session, flash, url_for
import mysql.connector
from mysql.connector import Error

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
            flash('Login Successful!', 'success')
            return redirect('/student_info')
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

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT attended_classes, total_classes FROM attendance WHERE student_Reg_No = %s", (reg_number,))
        attendance_data = cursor.fetchone()

        if attendance_data:
            attended = attendance_data['attended_classes']
            total = attendance_data['total_classes']
            status = 'eligible' if attended / total > 0.75 else 'fine' if attended / total > 0.5 else 'not_eligible'
            attendance = {
                'attended': attended,
                'total': total,
                'status': status
            }
            return render_template('attendance.html', attendance=attendance)
        else:
            flash('Attendance record not found.', 'danger')
            return redirect('/student_info')
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
        cursor.execute("SELECT subject, CIE_1, CIE_2, SEE FROM marks_sheet WHERE Reg_number = %s", (reg_number,))
        marks_data = cursor.fetchall()

        cursor.execute("SELECT Name, Reg_number, Course, Semester FROM student_info WHERE Reg_number = %s", (reg_number,))
        student_data = cursor.fetchone()

        if marks_data:
            total_marks = 0
            max_marks = 100
            calculated_marks = []

            for mark in marks_data:
                cie_1 = mark['CIE_1']
                cie_2 = mark['CIE_2']
                see = mark['SEE']

                scaled_cie_1 = round((cie_1 / 30) * 15)
                scaled_cie_2 = round((cie_2 / 30) * 15)

                if see > 60:
                    see = (see / 100) * 60

                subject_marks = scaled_cie_1 + scaled_cie_2 + see
                total_marks += subject_marks

                calculated_marks.append({
                    'subject': mark['subject'],
                    'obtained': int(subject_marks)
                })

            rounded_total_marks = round(total_marks)
            percentage = (total_marks / max_marks) * 100
            result = 'Pass' if percentage >= 40 else 'Fail'

            return render_template(
                'marks.html', 
                marks=calculated_marks, 
                total_marks=rounded_total_marks,  
                max_marks=max_marks, 
                percentage=round(percentage, 1),  
                result=result, 
                student=student_data
            )
        else:
            flash('No marks record found.', 'danger')
            return redirect('/student_info')
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
            return render_template('seat_allocation.html', allocation_exists=False)

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

        # Set rows to exactly 9
        rows = 9  

        return render_template(
            'seat_allocation.html', 
            allocation_exists=True, 
            reg_number=reg_number, 
            total_seats=total_seats, 
            seat_allocation=seat_allocation, 
            rows=rows, 
            seat_number=seat_number
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
        cursor.execute("SELECT Date, Subject, Course, StartTime, EndTime FROM timetable")
        results = cursor.fetchall()

        return render_template('exam_timetable.html', results=results)

    except Error as e:
        flash(f'Error fetching exam timetable: {e}', 'danger')
        return redirect('/student_info')
    
    finally:
        cursor.close()
        conn.close()


@app.route('/exam_registration', methods=['GET', 'POST'])
def exam_registration():
    if 'AE' not in session:
        session['AE'] = 0  # Attendance status session value

    fine = 2000 if session['AE'] == 1 else 0  # Fine for low attendance

    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/student_info')

    cursor = conn.cursor()

    try:
        # Fetch available subjects for registration
        cursor.execute("SELECT subject FROM subjects")
        subjects = cursor.fetchall()

        if request.method == 'POST':
            selected_subjects = request.form.getlist('subjects')
            if not selected_subjects:
                flash('Please select at least one subject.', 'danger')
                return redirect('/exam_registration')

            # Calculate total fee based on subjects selected
            fee_per_subject = 500  # Example fee per subject
            total_fee = len(selected_subjects) * fee_per_subject + fine

            session['subjects'] = selected_subjects
            session['fee'] = total_fee

            flash(f'Registration successful! Total fee: Rs {total_fee}', 'success')
            return redirect('/payment_options')

        return render_template('exam_registration.html', subjects=subjects, fine=fine)

    except Error as e:
        flash(f'Error fetching subjects: {e}', 'danger')
        return redirect('/student_info')

    finally:
        cursor.close()
        conn.close()


@app.route('/payment_options')
def payment_options():
    return render_template('payment_options.html')

@app.route('/process_payment', methods=['POST'])
def process_payment():
    error = False
    card_number = request.form.get('cn')
    expiration_date = request.form.get('ed')
    cvv = request.form.get('cvv')
    first_name = request.form.get('fn')
    last_name = request.form.get('ln')
    upi_id = request.form.get('upi')

    if card_number and expiration_date and cvv and first_name and last_name:
        return redirect(url_for('receipt'))
    elif upi_id:
        return redirect(url_for('receipt'))
    else:
        error = True
        return render_template('payment_options.html', error=error)

@app.route('/receipt')
def receipt():
    rn = session.get('rn', 'Unknown')
    fee = session.get('fee', 0)
    subjects = session.get('subjects', [])

    # MySQL insert to fee_payment table
    connection = get_db_connection()
    if connection is None:
        flash('Database connection failed!', 'danger')
        return redirect('/')

    try:
        cursor = connection.cursor()

        # Create the table if it doesn't exist
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS fee_payment (
            Reg_number VARCHAR(20),
            PStatus VARCHAR(20)
        )
        '''
        cursor.execute(create_table_query)

        # Insert payment record
        insert_payment_query = 'INSERT INTO fee_payment (Reg_number, PStatus) VALUES (%s, %s)'
        cursor.execute(insert_payment_query, (rn, 'Paid'))

        connection.commit()  # Commit the transaction

    except Error as e:
        flash(f'Error creating fee_payment table or inserting data: {e}', 'danger')
        return redirect('/payment_options')

    finally:
        cursor.close()
        connection.close()

    return render_template('receipt.html', fee=fee, subjects=subjects, rn=rn)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)