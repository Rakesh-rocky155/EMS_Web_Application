from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import create_marks_sheet, drop_marks_sheet, get_db_connection

main = Blueprint('main', __name__)

@main.route('/set_marks', methods=['GET', 'POST'])
def set_marks():
    create_marks_sheet()  # Ensure table exists
    if request.method == 'POST':
        reg_number = request.form['rn']
        subject = request.form['Sub']
        exam_type = request.form['o']
        marks = request.form['m']

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM marks_sheet WHERE Reg_number=%s AND Subject=%s", (reg_number, subject))
        result = cursor.fetchone()

        if result:
            flash("Record exists. Please update instead.", "warning")
            return redirect(url_for('main.set_marks'))

        if exam_type == "IA1":
            cursor.execute("INSERT INTO marks_sheet (Reg_number, Subject, IA1) VALUES (%s, %s, %s)", (reg_number, subject, marks))
        elif exam_type == "IA2":
            cursor.execute("INSERT INTO marks_sheet (Reg_number, Subject, IA2) VALUES (%s, %s, %s)", (reg_number, subject, marks))
        elif exam_type == "Final":
            cursor.execute("INSERT INTO marks_sheet (Reg_number, Subject, Final) VALUES (%s, %s, %s)", (reg_number, subject, marks))

        connection.commit()
        cursor.close()
        connection.close()
        flash("Marks Added Successfully!", "success")
        return redirect(url_for('main.set_marks'))

    return render_template('set_marks.html')

@main.route('/clear_marks', methods=['POST'])
def clear_marks():
    drop_marks_sheet()
    flash("All Marks Sheet records are cleared", "success")
    return redirect(url_for('main.set_marks'))

@main.route('/display_marks', methods=['GET'])
def display_marks():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM marks_sheet")
    marks = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('display_marks.html', marks=marks)

@main.route('/student_card/<reg_number>', methods=['GET'])
def student_card(reg_number):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM marks_sheet WHERE Reg_number=%s", (reg_number,))
    marks = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('student_card.html', marks=marks)
