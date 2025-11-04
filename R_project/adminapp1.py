from flask import Flask, render_template, request, redirect, url_for, flash, session, make_response
import os
from functools import wraps
from myapp import get_db_connection, set_attendance, view_attendance  # Importing functions from myapp
from markapp import set_marks, display_marks, clear_marks_records, clear_particular_marks
from seatapp import set_seats, set_individual_seat, allocate_multiple_course_seats, view_seats, clear_seats
from subapp import set_subjects, clear_all_subjects, clear_branch_subjects, clear_specific_subject, clear_subjects
from payapp import fee_payment_status, clear_fee_payment
from app import set_timetable, update_timetable, display_timetable, clear_timetable

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hard-coded user credentials (replace with a proper database in production)
users = {"Rakesh": "rocky"}

# Prevent caching for all requests to avoid accessing pages after logout
@app.before_request
def no_cache():
    response = make_response()
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Decorator to check if user is logged in
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['un']
        password = request.form['pw']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    return render_template('login.html')  # Create this HTML file

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])  # Create this HTML file

# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)  # Clears the session
    flash("You have been logged out.", "info")
    response = make_response(redirect(url_for('login')))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Protected routes
@app.route('/set_attendance', methods=['GET', 'POST'])
@login_required
def handle_set_attendance():
    return set_attendance()  # Call the imported function

@app.route('/view_attendance', methods=['GET', 'POST'])
@login_required
def handle_view_attendance():
    return view_attendance()  # Call the imported function

@app.route('/delete_record', methods=['POST'])
@login_required
def delete_record():
    student_Reg_No = request.form['student_Reg_No']
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('handle_view_attendance'))

        cursor = conn.cursor()
        cursor.execute('DELETE FROM attendance WHERE student_Reg_No = %s', (student_Reg_No,))
        conn.commit()
        cursor.close()
        conn.close()

        flash("Record successfully deleted!", 'success')
    except Exception as err:  # Catch all exceptions
        flash(f"Error: {err}", 'error')

    return redirect(url_for('handle_view_attendance'))

@app.route('/clear_records', methods=['POST'])
@login_required
def clear_records():
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('handle_view_attendance'))

        cursor = conn.cursor()
        cursor.execute('DELETE FROM attendance')
        conn.commit()
        cursor.close()
        conn.close()

        flash("All records cleared successfully!", 'success')
    except Exception as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('handle_view_attendance'))

# Additional routes for other functionalities
@app.route('/set_marks', methods=['GET', 'POST'])
@login_required
def handle_set_marks():
    if request.method == 'POST':
        return set_marks()
    return render_template('set_marks.html')  # Create this HTML file

@app.route('/view_marks', methods=['GET', 'POST'])
@login_required
def handle_view_marks():
    return display_marks()

@app.route('/clear_marks', methods=['POST'])
@login_required
def handle_clear_marks():
    return clear_marks_records()

@app.route('/clear_particular_marks', methods=['POST'])
@login_required
def handle_clear_particular_marks():
    return clear_particular_marks()

@app.route('/allot_examination_seats', methods=['GET', 'POST'])
@login_required
def allot_examination_seats():
    return set_seats()

@app.route('/allot_individual_seat', methods=['POST'])
@login_required
def allot_individual_seat():
    return set_individual_seat()

@app.route('/allot_multiple_course_seat', methods=['POST'])
@login_required
def allot_multiple_course_seat():
    return allocate_multiple_course_seats()

@app.route('/view_examination_seats')
@login_required
def view_examination_seats():
    return view_seats()

@app.route('/clear_seat_records', methods=['POST'])
@login_required
def clear_seat_records():
    return clear_seats()

@app.route('/sets_subjects', methods=['GET', 'POST'])
@login_required
def sets_subjects():
    return set_subjects()

@app.route('/clears_subjects', methods=['GET'])
@login_required
def clears_subjects():
    return clear_subjects()

@app.route('/clears_all_subjects', methods=['POST'])
@login_required
def clears_all_subjects():
    return clear_all_subjects()

@app.route('/clears_specific_subject', methods=['POST'])
@login_required
def clears_specific_subject():
    return clear_specific_subject()

@app.route('/clears_branch_subjects', methods=['POST'])
@login_required
def clears_branch_subjects():
    return clear_branch_subjects()

@app.route('/fees_payment_status')
@login_required
def fees_payment_status():
    return fee_payment_status()

@app.route('/clears_fee_payment')
@login_required
def clears_fee_payment():
    return clear_fee_payment()

@app.route('/sets_timetable', methods=['GET', 'POST'])
@login_required
def sets_timetable():
    return set_timetable()

@app.route('/updates_timetable', methods=['GET', 'POST'])
@login_required
def updates_timetable():
    return update_timetable()

@app.route('/view_timetable', methods=['GET', 'POST'])
@login_required
def view_timetable():
    return display_timetable()

@app.route('/clears_timetable', methods=['POST'])
@login_required
def clears_timetable():
    return clear_timetable()

@app.route('/test')
def test():
    return "Test route is working!"


if __name__ == '__main__':
    app.run(debug=True)
