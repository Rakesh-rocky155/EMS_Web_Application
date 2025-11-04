from flask import Flask, request, render_template, redirect, flash
import MySQLdb

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def db_connection():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="exam_management")

# Route to display seat allocation records
@app.route('/')
def seat_allocation_display():
    con = db_connection()
    cur = con.cursor()

    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    verify = any(table[0] == 'seat_allocation' for table in tables)

    if not verify:
        flash('No seat allocation records exist')
        return redirect('/info')

    cur.execute("SELECT DISTINCT Classroom_number FROM seat_allocation")
    classroom_numbers = cur.fetchall()
    total_pages = len(classroom_numbers)

    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1
    elif page > total_pages:
        page = total_pages

    cur.execute(f"SELECT * FROM seat_allocation WHERE Classroom_number={page} ORDER BY seat_number")
    seat_allocation = cur.fetchall()
    
    total_seats = len(seat_allocation)
    seat_array = ['x' if i != seat[2] - 1 else seat[0] for i, seat in enumerate(seat_allocation)]
    
    con.close()
    return render_template('seat_allocation_display.html', current_page=page, total_pages=total_pages, seat_array=seat_array, total_seats=total_seats)

# Route to set seat allocation
@app.route('/set_seat_allocation', methods=['GET', 'POST'])
def set_seat_allocation():
    if request.method == 'POST':
        course = request.form.get('c')
        num_students = int(request.form.get('ns'))

        con = db_connection()
        cur = con.cursor()

        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        verify = any(table[0] == 'seat_allocation' for table in tables)

        if not verify:
            cur.execute("""
                CREATE TABLE seat_allocation(
                    Reg_number VARCHAR(20),
                    Classroom_number INT(20),
                    Seat_number INT(20)
                )
            """)

        cur.execute("SELECT number_of_seats FROM classroom_size")
        classroom_size = cur.fetchall()

        cur.execute(f"SELECT * FROM course_rn WHERE Course='{course}'")
        course_data = cur.fetchone()
        reg_prefix = course_data[1]

        reg_num = 20001
        for i in range(1, num_students + 1):
            if reg_num <= classroom_size[i - 1][0]:
                classroom_num = i
                seat_num = i
                cur.execute(f"INSERT INTO seat_allocation VALUES ('{reg_prefix}{reg_num}', {classroom_num}, {seat_num})")
                reg_num += 1

        con.commit()
        con.close()
        flash(f'Seats allotted for {course} students')
        return redirect('/set_seat_allocation')

    return render_template('seat_allocation_set.html')

# Route to clear seat allocation records
@app.route('/clear_records')
def clear_records():
    con = db_connection()
    cur = con.cursor()

    cur.execute("SHOW TABLES")
    tables = cur.fetchall()
    verify = any(table[0] == 'seat_allocation' for table in tables)

    if verify:
        cur.execute("DROP TABLE seat_allocation")
        con.commit()
        flash('All seat allocation records cleared')
    else:
        flash('No records exist to clear')

    con.close()
    return redirect('/set_seat_allocation')

if __name__ == '__main__':
    app.run(debug=True)
