from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Database connection setup with environment variables
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),  # your password should be set in the environment
            database=os.getenv('DB_NAME', 'exam_management'),  # updated database name
            port=int(os.getenv('DB_PORT', 3306))  # optional port setting, defaults to 3306
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Route for setting attendance
@app.route('/set_attendance', methods=['GET', 'POST'])
def set_attendance():
    if request.method == 'POST':
        # Retrieve form data
        student_Reg_No = request.form.get('student_Reg_No')
        student_name = request.form.get('student_name')
        subject = request.form.get('subject')
        attended_classes = request.form.get('attended_classes')
        total_classes = request.form.get('total_classes')

        # Validate form data
        if not student_Reg_No or not student_name or not subject or not attended_classes or not total_classes:
            flash("Please fill in all the fields!", 'error')
            return redirect(url_for('set_attendance'))

        try:
            # Establish database connection and insert or update data
            conn = get_db_connection()
            if conn is None:
                flash("Database connection error!", 'error')
                return redirect(url_for('handle_set_attendance'))

            cursor = conn.cursor()

            # Check if record already exists
            check_sql = '''
                SELECT * FROM attendance 
                WHERE student_Reg_No = %s AND subject = %s
            '''
            cursor.execute(check_sql, (student_Reg_No, subject))
            existing_record = cursor.fetchone()

            if existing_record:
                # Update existing attendance record
                update_sql = '''
                    UPDATE attendance 
                    SET attended_classes = %s, total_classes = %s 
                    WHERE student_Reg_No = %s AND subject = %s
                '''
                cursor.execute(update_sql, (attended_classes, total_classes, student_Reg_No, subject))
                flash(f"Attendance for {subject} of updated successfully!", 'success')
            else:
                # Insert new attendance record
                insert_sql = '''
                    INSERT INTO attendance (student_Reg_No, student_name, subject, attended_classes, total_classes)
                    VALUES (%s, %s, %s, %s, %s)
                '''
                cursor.execute(insert_sql, (student_Reg_No, student_name, subject, attended_classes, total_classes))
                flash(f"Attendance for {subject} added successfully!", 'success')

            conn.commit()
            cursor.close()
            conn.close()

        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'error')

    # Render the attendance form if GET request
    return render_template('set_attendance.html')



# Route for viewing attendance
@app.route('/view_attendance', methods=['GET', 'POST'])
def view_attendance():
    attendance_records = None  # Initialize variable for handling GET requests
    subject = None
    

    if request.method == 'POST':
        subject = request.form['subject']  # Get selected subject from form

        # Establish database connection
        con = get_db_connection()
        cursor = con.cursor()

        # Fetch attendance records for the selected subject
        cursor.execute(
            'SELECT student_Reg_No, student_name, subject, attended_classes, total_classes '
            'FROM attendance WHERE subject=%s ORDER BY student_Reg_No', (subject,))
        attendance_records = cursor.fetchall()  # Assign fetched records

        cursor.close()
        con.close()

        # Flash a message if no records are found for the given subject
        #if not attendance_records:
            #flash(f"No attendance records found for the subject {subject}.", 'info')

    # Pass subject to the template whether or not attendance_records are found
    return render_template('view_attendance.html', attendance_records=attendance_records, subject=subject)

# Route for clearing attendance records
@app.route('/delete_record', methods=['POST'])
def delete_record():
    student_Reg_No = request.form['student_Reg_No']

    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('view_attendance'))

        cursor = conn.cursor()
        cursor.execute('DELETE FROM attendance WHERE student_Reg_No = %s', (student_Reg_No,))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Record successfully deleted!", 'success')
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('view_attendance'))



# Route to clear all records
# Route to clear all records for a specific subject
@app.route('/clear_records', methods=['POST'])
def clear_records():
    subject = request.form['subject']
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('view_attendance'))

        cursor = conn.cursor()
        # Corrected SQL query to delete records for the specified subject
        cursor.execute('DELETE FROM attendance WHERE subject = %s', (subject,))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"All records for subject '{subject}' cleared successfully!", 'success')
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('view_attendance'))



if __name__ == '__main__':
    app.run(debug=True)

