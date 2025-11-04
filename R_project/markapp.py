from flask import Flask, render_template, request, redirect, flash, url_for
import MySQLdb  # Import the MySQLdb module

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# MySQL Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'passwd': '',  # Change this to your MySQL root password if applicable
    'db': 'exam_management'
}

@app.route('/set_marks', methods=['GET', 'POST'])
def set_marks():
    if request.method == 'POST':
        reg_number = request.form.get('Reg_number')
        subject = request.form.get('subject')
        exam_type = request.form.get('exam_type')
        marks = request.form.get('marks')

        if not reg_number or not subject or not marks:
            flash('Registration Number, Subject, and Marks are required.', 'danger')
            return redirect(url_for('set_marks'))

        conn = MySQLdb.connect(**db_config)
        cur = conn.cursor()

        # Check if record exists for the same reg_number and subject
        cur.execute("SELECT * FROM marks_sheet WHERE Reg_number = %s AND subject = %s", (reg_number, subject))
        existing_marks = cur.fetchone()

        if existing_marks:
            flash('Marks already exist. Updating...', 'warning')
            # Update the specific exam type field (CIE_1, CIE_2, or SEE)
            cur.execute(f"""
                UPDATE marks_sheet 
                SET {exam_type} = %s
                WHERE Reg_number = %s AND subject = %s
                """, (marks, reg_number, subject))
            conn.commit()
            flash(f'{exam_type} Marks Updated Successfully', 'success')
        else:
            # Insert new record with the specified exam type and marks
            cur.execute(f"""
                INSERT INTO marks_sheet (Reg_number, subject, {exam_type}) 
                VALUES (%s, %s, %s)
                """, (reg_number, subject, marks))
            conn.commit()
            flash(f'{exam_type} Marks Added Successfully', 'success')

        cur.close()
        conn.close()
        return redirect(url_for('handle_set_marks'))

    return render_template('set_marks.html')


@app.route('/clear_records', methods=['POST'])
def clear_marks_records():
    subject = request.form.get('subject')  # Get the subject from the form

    if not subject:
        flash('Subject is required to clear specific records.', 'danger')
        return redirect(url_for('handle_view_marks'))

    conn = MySQLdb.connect(**db_config)
    cur = conn.cursor()

    # Delete only the records for the specific subject
    cur.execute("DELETE FROM marks_sheet WHERE subject = %s", (subject,))
    conn.commit()

    cur.close()
    conn.close()
    flash(f'All records for {subject} cleared successfully.', 'success')
    return redirect(url_for('handle_view_marks'))


@app.route('/clear_particular_marks', methods=['POST'])
def clear_particular_marks():
    reg_number = request.form.get('Reg_number')
    subject = request.form.get('subject')

    if not reg_number or not subject:
        flash('Both Registration Number and Subject are required to delete a specific record.', 'danger')
        return redirect(url_for('handle_view_marks'))

    conn = MySQLdb.connect(**db_config)
    cur = conn.cursor()

    cur.execute("DELETE FROM marks_sheet WHERE Reg_number = %s AND subject = %s", (reg_number, subject))
    conn.commit()

    cur.close()
    conn.close()

    flash(f'Marks for {reg_number} in {subject} cleared successfully.', 'success')
    return redirect(url_for('handle_view_marks'))


@app.route('/display_marks', methods=['GET', 'POST'])
def display_marks():
    marks_list = []  # Initialize list for GET requests
    subject = None  # Initialize subject to None for GET requests

    if request.method == 'POST':
        subject = request.form['subject']  # Get subject from form

        # Establish database connection and handle potential errors
        try:
            conn = MySQLdb.connect(**db_config)
            cur = conn.cursor()

            # Fetch marks data for the given subject
            cur.execute("SELECT Reg_number, subject, CIE_1, CIE_2, Event, SEE FROM marks_sheet WHERE subject=%s ORDER BY Reg_number", (subject,))
            marks_data = cur.fetchall()

            # Prepare a list of dictionaries for template rendering
            for row in marks_data:
                marks_list.append({
                    'Reg_number': row[0],
                    'subject': row[1],
                    'CIE_1': row[2] if row[2] is not None else 0,
                    'CIE_2': row[3] if row[3] is not None else 0,
                    'Event': row[4] if row[4] is not None else 0,
                    'SEE': row[5] if row[5] is not None else 0,
                    'Total': (row[2] or 0) + (row[3] or 0) + (row[4] or 0) + (row[5] or 0)  # Calculate total
                })
        except MySQLdb.Error as e:
            flash("An error occurred while fetching marks data.")
            print("Database error:", e)  # Debugging information
        finally:
            # Ensure resources are properly released
            cur.close()
            conn.close()

    # Render the template with the marks data or an empty list if no POST request was made
    return render_template('display_marks.html', marks_sheet=marks_list, subject=subject)




if __name__ == '__main__':
    app.run(debug=True)