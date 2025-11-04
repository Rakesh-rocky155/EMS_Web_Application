from flask import Flask, render_template, redirect, url_for, flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure key

# Database connection configuration
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="exam_management"
    )

@app.route('/clear_fee_payment')
def clear_fee_payment():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        # Check if the fee_payment table exists
        if ('fee_payment',) in tables:
            cursor.execute("DROP TABLE fee_payment")
            con.commit()
            flash('All Fee Payment records are cleared')
        else:
            flash('No records exist to clear')

    except mysql.connector.Error as err:
        flash('Fee Payment could not be cleared due to technical problems')
    finally:
        cursor.close()
        con.close()

    return fee_payment_status()  # Call the fee_payment_status view directly

@app.route('/fee_payment_status')
def fee_payment_status():
    try:
        con = get_db_connection()
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        if ('fee_payment',) not in tables:
            flash('No Fee Payment records exist')
            return render_template('fee_payment_status.html', fee_status=[])

        cursor.execute("SELECT * FROM student_info ORDER BY Reg_number")
        students = cursor.fetchall()

        # Prepare fee status for each student
        fee_status = []
        for student in students:
            cursor.execute("SELECT * FROM fee_payment WHERE Reg_number=%s", (student[0],))
            payment_records = cursor.fetchall()
            status = "Paid" if payment_records else "Not Paid"
            fee_status.append((student[1], student[0], student[2], student[3], status))

    except mysql.connector.Error as err:
        fee_status = []
        flash('Error retrieving fee payment status')
    finally:
        cursor.close()
        con.close()

    return render_template('fee_payment_status.html', fee_status=fee_status)

@app.route('/info_page')
def info_page():
    return render_template('info_page.html')  # Implement this template

if __name__ == '__main__':
    app.run(debug=True)
