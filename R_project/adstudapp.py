from flask import Flask, render_template, request, redirect, flash, session, url_for
import MySQLdb

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Set your secret key here

# Database connection
def get_db_connection():
    return MySQLdb.connect(user='your_user', passwd='your_password', db='your_database', host='localhost')

# Home route (login and registration page)
@app.route('/')
def login_register():
    return render_template('login_and_register.html')

# Handling login for admin and student
@app.route('/login', methods=['POST'])
def login():
    reg_number = request.form['reg_number']
    password = request.form['password']
    role = request.form['role']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check login based on role
    if role == 'admin':
        cursor.execute("SELECT * FROM admin WHERE reg_number = %s AND password = %s", (reg_number, password))
    else:
        cursor.execute("SELECT * FROM student_info WHERE reg_number = %s AND password = %s", (reg_number, password))

    user = cursor.fetchone()
    conn.close()

    if user:
        # Store login session
        session['user_role'] = role
        session['reg_number'] = reg_number

        flash(f"Welcome, {role.capitalize()} {reg_number}!", "success")

        # Redirect based on role
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('student_dashboard'))
    else:
        flash("Invalid credentials, please try again.", "danger")
        return redirect('/')

# Admin dashboard
@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('user_role') == 'admin':
        return render_template('admin_dashboard.html')
    else:
        flash("Unauthorized access!", "danger")
        return redirect('/')

# Student dashboard
@app.route('/student_dashboard')
def student_dashboard():
    if session.get('user_role') == 'student':
        reg_number = session['reg_number']
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch student info
        cursor.execute("SELECT * FROM student_info WHERE reg_number = %s", (reg_number,))
        student = cursor.fetchone()

        conn.close()
        return render_template('student_dashboard.html', student=student)
    else:
        flash("Unauthorized access!", "danger")
        return redirect('/')

# Handling student registration
@app.route('/register_student', methods=['POST'])
def register_student():
    name = request.form['name']
    reg_number = request.form['reg_number']
    course = request.form['course']
    semester = request.form['semester']
    password = request.form['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert student data into student_info table
    cursor.execute("""
        INSERT INTO student_info (name, reg_number, course, semester, password)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, reg_number, course, semester, password))

    conn.commit()
    conn.close()

    flash(f"Student {name} registered successfully!", "success")
    return redirect('/')

# Logout route
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out!", "info")
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
