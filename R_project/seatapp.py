from flask import Flask, render_template, request, redirect, session, url_for, flash
import MySQLdb

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Database connection
def connect_db():
    return MySQLdb.connect(host="localhost", user="root", passwd="", db="exam_management")

# Route to set seats page
@app.route('/set_seats', methods=['GET', 'POST'])
def set_seats():
    return render_template('set_seats.html')

# Route to set individual seat allocation
@app.route('/set_individual_seat', methods=['POST'])
def set_individual_seat():
    reg_number = request.form['Reg_number']
    classroom_number = str(request.form['Classroom_number'])
    seat_number = request.form['Seat_number']

    try:
        with connect_db() as db:
            cursor = db.cursor()
            
            # Check for seat conflict
            cursor.execute("""
                SELECT * FROM seat_allocation 
                WHERE Classroom_number = %s AND Seat_number = %s AND Reg_number != %s
            """, (classroom_number, seat_number, reg_number))
            conflicting_allocation = cursor.fetchone()

            if conflicting_allocation:
                # Flash a message and set a session flag to show the confirmation dialog
                flash('This seat is already assigned to another student.')
                session['seat_conflict'] = {
                    'reg_number': reg_number,
                    'classroom_number': classroom_number,
                    'seat_number': seat_number
                }
                return redirect(url_for('allot_examination_seats'))

            # Proceed with regular seat allocation if no conflict
            cursor.execute("SELECT * FROM seat_allocation WHERE Reg_number = %s", (reg_number,))
            existing_allocation = cursor.fetchone()

            if existing_allocation:
                cursor.execute("""
                    UPDATE seat_allocation 
                    SET Classroom_number=%s, Seat_number=%s 
                    WHERE Reg_number=%s
                """, (classroom_number, seat_number, reg_number))
                flash('Seat allocation updated successfully!')
            else:
                cursor.execute("""
                    INSERT INTO seat_allocation (Reg_number, Classroom_number, Seat_number) 
                    VALUES (%s, %s, %s)
                """, (reg_number, classroom_number, seat_number))
                flash('New seat allocated successfully!')

            db.commit()

    except MySQLdb.Error as e:
        flash(f'Error while processing seat allocation: {e}')

    return redirect(url_for('allot_examination_seats'))


# Route to allocate seats for multiple courses with gaps in registration numbers
@app.route('/allocate_multiple_course_seats', methods=['POST'])
def allocate_multiple_course_seats():
    first_course_name = request.form['First_Course_name']
    number_of_students_first = int(request.form['Number_of_Students_First'])
    starting_reg_number_first = request.form['Starting_Reg_Number_First']
    classroom_number_first = str(request.form['Classroom_Number_First'])

    second_course_name = request.form['Second_Course_name']
    number_of_students_second = int(request.form['Number_of_Students_Second'])
    starting_reg_number_second = request.form['Starting_Reg_Number_Second']
    classroom_number_second = str(request.form['Classroom_Number_Second'])

    try:
        with connect_db() as db:
            cursor = db.cursor()
            updated_count = 0
            new_count = 0

            # Allocate or update seats for the first course
            cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no = %s", (classroom_number_first,))
            result_first = cursor.fetchone()

            if result_first is None:
                flash(f'Classroom {classroom_number_first} not found.')
                return redirect(url_for('allot_examination_seats'))

            number_of_seats_first = result_first[0]

            if number_of_students_first > number_of_seats_first // 2:
                flash('Number of students exceeds the number of available seats for the first course.')
                return redirect(url_for('allot_examination_seats'))

            for i in range(number_of_students_first):
                reg_suffix = str(int(starting_reg_number_first[-3:]) + i).zfill(len(starting_reg_number_first[-3:]))
                new_reg_number_first = starting_reg_number_first[:-3] + reg_suffix
                seat_number = (i * 2) + 1  # Allocating seats 1, 3, 5...

                # Check if an allocation exists for this reg number and course
                cursor.execute("""
                    SELECT COUNT(*) FROM seat_allocation 
                    WHERE Reg_number = %s AND Classroom_number = %s
                """, (new_reg_number_first, classroom_number_first))
                exists = cursor.fetchone()[0]

                if exists:
                    cursor.execute("""
                        UPDATE seat_allocation SET Seat_number = %s 
                        WHERE Reg_number = %s AND Classroom_number = %s
                    """, (seat_number, new_reg_number_first, classroom_number_first))
                    updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO seat_allocation (Reg_number, Classroom_number, Seat_number) 
                        VALUES (%s, %s, %s)
                    """, (new_reg_number_first, classroom_number_first, seat_number))
                    new_count += 1

            # Allocate or update seats for the second course
            cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no = %s", (classroom_number_second,))
            result_second = cursor.fetchone()

            if result_second is None:
                flash(f'Classroom {classroom_number_second} not found.')
                return redirect(url_for('allot_examination_seats'))

            number_of_seats_second = result_second[0]

            if number_of_students_second > number_of_seats_second // 2:
                flash('Number of students exceeds the number of available seats for the second course.')
                return redirect(url_for('allot_examination_seats'))

            for i in range(number_of_students_second):
                reg_suffix = str(int(starting_reg_number_second[-3:]) + i).zfill(len(starting_reg_number_second[-3:]))
                new_reg_number_second = starting_reg_number_second[:-3] + reg_suffix
                seat_number = (i * 2) + 2  # Allocating seats 2, 4, 6...

                cursor.execute("""
                    SELECT COUNT(*) FROM seat_allocation 
                    WHERE Reg_number = %s AND Classroom_number = %s
                """, (new_reg_number_second, classroom_number_second))
                exists = cursor.fetchone()[0]

                if exists:
                    cursor.execute("""
                        UPDATE seat_allocation SET Seat_number = %s 
                        WHERE Reg_number = %s AND Classroom_number = %s
                    """, (seat_number, new_reg_number_second, classroom_number_second))
                    updated_count += 1
                else:
                    cursor.execute("""
                        INSERT INTO seat_allocation (Reg_number, Classroom_number, Seat_number) 
                        VALUES (%s, %s, %s)
                    """, (new_reg_number_second, classroom_number_second, seat_number))
                    new_count += 1

            db.commit()
            flash(f'Successfully allocated {new_count} new seats and updated {updated_count} existing seats for {first_course_name} and {second_course_name}.')

    except MySQLdb.Error as e:
        flash(f'Error while allocating course seats: {e}')

    return redirect(url_for('allot_examination_seats'))


# Route to view allocated seats
@app.route('/view_seats')
def view_seats():
    try:
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM seat_allocation")
            allocated_seats = cursor.fetchall()

            if not allocated_seats:
               flash("No seats have been allocated yet!", 'info')
    except MySQLdb.Error as e:
        flash(f'Error retrieving seat allocation: {e}')
        allocated_seats = []

    return render_template('view_seats.html', allocated_seats=allocated_seats)

# Route to clear all seat allocations or individual
@app.route('/clear_seats', methods=['POST'])
def clear_seats():
    reg_number = request.form.get('Reg_number')  
    try:
        with connect_db() as db:
            cursor = db.cursor()
            if reg_number:
                cursor.execute("DELETE FROM seat_allocation WHERE Reg_number = %s", (reg_number,))
                flash(f'Seat allocation for registration number {reg_number} cleared.')
            else:
                cursor.execute("DELETE FROM seat_allocation")
                flash('All seat allocations cleared.')
            db.commit()

    except MySQLdb.Error as e:
        flash(f'Error clearing seats: {e}')

    return redirect(url_for('view_examination_seats'))

if __name__ == '__main__':
    app.run(debug=True)
