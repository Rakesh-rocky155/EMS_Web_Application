from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from datetime import datetime, timedelta

import pymysql

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="exam_management"
    )

# Set timetable route
from datetime import datetime, timedelta

@app.route('/set_timetable', methods=['GET', 'POST'])
def set_timetable():
    if request.method == 'POST':
        course = request.form['course']
        sem = request.form['sem']
        start_date = request.form['start_date']
        start_time = request.form['start_time']
        
        con = get_db_connection()
        cursor = con.cursor()

        # Check if timetable table exists
        cursor.execute("SHOW TABLES LIKE 'timetable'")
        timetable_exists = cursor.fetchone()

        # If timetable doesn't exist, create it
        if not timetable_exists:
            cursor.execute(""" 
                CREATE TABLE timetable (
                    Course VARCHAR(20),
                    Sem INT,
                    Subject VARCHAR(20),
                    Date DATE,
                    StartTime TIME,
                    EndTime TIME
                )
            """)
            con.commit()

        # Delete old entries for the course and semester
        cursor.execute("DELETE FROM timetable WHERE Course=%s AND Sem=%s", (course, sem))

        # Get subjects for the course
        cursor.execute("SELECT * FROM subjects WHERE Course=%s AND Sem=%s", (course, sem))
        subjects = cursor.fetchall()

        if subjects:
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_time_obj = datetime.strptime(start_time, '%H:%M')

            for subject in subjects:
                date_str = current_date.strftime('%Y-%m-%d')
                end_time_obj = start_time_obj + timedelta(hours=3)

                # Insert new entry with correct time format
                cursor.execute(
                    "INSERT INTO timetable (Date, Subject, Course, Sem, StartTime, EndTime) VALUES (%s, %s, %s, %s, %s, %s)",
                    (date_str, subject[2], course, sem, start_time_obj.strftime('%H:%M:%S'), end_time_obj.strftime('%H:%M:%S'))
                )

                # Adjust date (skip weekends)
                if current_date.weekday() == 4:  # If Friday, skip 3 days
                    current_date += timedelta(days=3)
                else:
                    current_date += timedelta(days=2)

            con.commit()
            flash(f"Timetable set for {course} - Semester {sem}", 'success')
        else:
            flash(f"No subjects found for {course} - Semester {sem}", 'danger')

        cursor.close()
        con.close()
        return redirect(url_for('sets_timetable'))
    
    return render_template('set_timetable.html')

# Update timetable route
@app.route('/update_timetable', methods=['GET', 'POST'])
def update_timetable():
    if request.method == 'POST':
        course = request.form['course']
        sem = request.form['sem']
        start_date = request.form['start_date']
        start_time = request.form['start_time']

        con = get_db_connection()
        cursor = con.cursor()

        # Delete old entries for the course and semester
        cursor.execute("DELETE FROM timetable WHERE Course=%s AND Sem=%s", (course, sem))

        # Get subjects for the course
        cursor.execute("SELECT * FROM subjects WHERE Course=%s AND Sem=%s", (course, sem))
        subjects = cursor.fetchall()

        if subjects:
            current_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_time_obj = datetime.strptime(start_time, '%H:%M')

            for subject in subjects:
                date_str = current_date.strftime('%Y-%m-%d')
                end_time_obj = start_time_obj + timedelta(hours=3)

                # Insert new entry with correct time format
                cursor.execute(
                    "INSERT INTO timetable (Date, Subject, Course, Sem, StartTime, EndTime) VALUES (%s, %s, %s, %s, %s, %s)",
                    (date_str, subject[2], course, sem, start_time_obj.strftime('%H:%M:%S'), end_time_obj.strftime('%H:%M:%S'))
                )

                # Adjust date (skip weekends)
                if current_date.weekday() == 4:
                    current_date += timedelta(days=3)
                else:
                    current_date += timedelta(days=2)

            con.commit()
            flash(f"Timetable updated for {course} - Semester {sem}", 'success')
        else:
            flash(f"No subjects found for {course} - Semester {sem}", 'danger')

        cursor.close()
        con.close()
        return redirect(url_for('update_timetable'))
    
    return render_template('update_timetable.html')


# Display timetable route
@app.route('/display_timetable', methods=['GET', 'POST'])
def display_timetable():
    timetable_data = None
    course = None
    sem = None

    if request.method == 'POST':
        # Retrieve input values from the form
        course = request.form.get('course')
        sem = request.form.get('sem')

        # Validate input
        if course and sem:
            try:
                # Connect to the database
                con = get_db_connection()
                cursor = con.cursor()

                # Fetch timetable records for the selected course and semester
                cursor.execute(
                    "SELECT Course, Sem, Subject, Date, StartTime, EndTime FROM timetable WHERE Course=%s AND Sem=%s ORDER BY Date",
                    (course, sem)
                )
                timetable_data = cursor.fetchall()

                cursor.close()
                con.close()

                # Check if any records were found
                if not timetable_data:
                    flash(f"No timetable found for {course} - Semester {sem}.", 'info')
                    return redirect(url_for('view_timetable'))
            except pymysql.MySQLError as e:
                # Handle specific database errors
                if e.args[0] == 1146:  # Table does not exist error code
                    flash("The timetable table does not exist. Please create the table first.", 'danger')
                else:
                    flash(f"An error occurred while fetching the timetable: {e}", 'danger')
                return redirect(url_for('view_timetable'))
            except Exception as e:
                # Generic error handling
                flash(f"An unexpected error occurred: {e}", 'danger')
                return redirect(url_for('view_timetable'))
        else:
            # Flash message if input is missing
            flash("Please select both course and semester to view the timetable.", 'warning')
            return redirect(url_for('view_timetable'))

    # Render the timetable display page
    return render_template('display_timetable.html', timetable_data=timetable_data, course=course, sem=sem)



# Clear timetable route
@app.route('/clear_timetable', methods=['POST'])
def clear_timetable():
    # Get the course and semester values from the form
    course = request.form.get('course')
    sem = request.form.get('sem')

    # Debugging: Print the values to check if they are being received correctly
    print(f"Course: {course}, Semester: {sem}")

    # Check if both course and semester are provided
    if course and sem:
        # Establish database connection
        con = get_db_connection()
        cursor = con.cursor()

        try:
            # Delete records for the specific course and semester
            cursor.execute("DELETE FROM timetable WHERE Course=%s AND Sem=%s", (course, sem))
            con.commit()

            # Provide feedback to the user
            flash(f"Timetable for {course} - Semester {sem} has been cleared.", 'info')

        except Exception as e:
            # Handle any database errors
            flash(f"An error occurred while clearing the timetable: {e}", 'error')
        
        finally:
            # Close the database connection
            cursor.close()
            con.close()

    else:
        # If course or semester is not provided, show a warning message
        flash("Please specify both course and semester to clear.", 'warning')

    # Redirect to the view_timetable route to show the updated timetable
    return redirect(url_for('view_timetable'))


# Run the app
if __name__ == '__main__':
    app.run(debug=True)
