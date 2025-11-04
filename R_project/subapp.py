from flask import Flask, render_template, request, redirect, url_for, flash
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flashing messages

# Connect to your database
def get_db_connection():
    conn = MySQLdb.connect(host="localhost", user="root", passwd="", db="exam_management")
    return conn

# Route for the Set Subjects page
@app.route('/set_subjects', methods=['GET', 'POST'])
def set_subjects():
    if request.method == 'POST':
        # Get the course name and subjects
        course = request.form['c']
        sem = request.form['sem']
        subject_count = int(request.form['subjectCount'])
        subjects = [request.form[f'subject{i+1}'] for i in range(subject_count)]

        # Insert subjects into the database
        conn = get_db_connection()
        cursor = conn.cursor()
        for subject in subjects:
            cursor.execute("INSERT INTO subjects (course, sem, subject) VALUES (%s, %s, %s)", (course, sem, subject))
        conn.commit()
        cursor.close()
        conn.close()

        # Flash a success message after subjects are added
        flash(f"Subjects successfully allocated for {course} - Semester {sem}.", 'success')

        return redirect(url_for('sets_subjects'))
    
    return render_template('set_subjects.html')


# Route to view subjects with filtering by course and semester
@app.route('/view_subjects', methods=['GET', 'POST'])
def view_subjects():
    subjects = []
    course = None
    sem = None
    no_subjects_message = None

    if request.method == 'POST':
        # Retrieve form data for filtering
        course = request.form.get('course')
        sem = request.form.get('sem')

        # Fetch subjects for the given course and semester
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT course, sem, subject FROM subjects WHERE course = %s AND sem = %s", (course, sem))
        subjects = cursor.fetchall()
        cursor.close()
        conn.close()

        # Check if no subjects are allocated for the given course and semester
        if not subjects:
            no_subjects_message = f"No subjects allocated for Course: '{course}' and Semester: '{sem}'."

    return render_template('view_subjects.html', subjects=subjects, course=course, sem=sem, no_subjects_message=no_subjects_message)


# Route to handle clearing a specific subject
@app.route('/clear_specific_subject', methods=['POST'])
def clear_specific_subject():
    course = request.form['course']
    subject = request.form['subject']
    sem = request.form['sem']
    
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('handle_view_subjects'))
        # Clear the specific subject from the course
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE course = %s AND sem = %s AND subject = %s", (course, sem, subject))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Subject '{subject}' cleared successfully from {sem} sem '{course}'!")  # Flash message
    except MySQLdb.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('handle_view_subjects'))  # Correct redirect

# Route to handle clearing subjects for a specific branch
@app.route('/clear_branch_subjects', methods=['POST'])
def clear_branch_subjects():
    branch = request.form['branch']
    sem = request.form['sem']
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('handle_view_subjects'))
        # Clear subjects for the specified branch
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subjects WHERE course = %s AND sem = %s", (branch, sem))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"All subjects cleared successfully for {sem} sem '{branch}'!")  # Flash message
    except MySQLdb.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('handle_view_subjects'))  # Correct redirect

if __name__ == '__main__':
    app.run(debug=True)
