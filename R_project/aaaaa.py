@app.route('/set_individual_seat', methods=['POST'])
def set_individual_seat():
    reg_number = request.form['Reg_number']
    classroom_number = request.form['Classroom_number']
    seat_number = request.form['Seat_number']

    try:
        with connect_db() as db:
            cursor = db.cursor()
            cursor.execute("SELECT * FROM seat_allocation WHERE Reg_number = %s", (reg_number,))
            existing_allocation = cursor.fetchone()

            if existing_allocation:
                cursor.execute("""UPDATE seat_allocation 
                                  SET Classroom_number=%s, Seat_number=%s 
                                  WHERE Reg_number=%s""",
                               (classroom_number, seat_number, reg_number))
                db.commit()
                flash('Seat allocation updated successfully!')
            else:
                cursor.execute("""INSERT INTO seat_allocation (Reg_number, Classroom_number, Seat_number) 
                                  VALUES (%s, %s, %s)""",
                               (reg_number, classroom_number, seat_number))
                db.commit()
                flash('New seat allocated successfully!')

    except MySQLdb.Error as e:
        flash(f'Error while processing seat allocation: {e}')

    return redirect(url_for('allot_examination_seats'))

# Route to allocate seats for multiple courses with gaps in registration numbers
@app.route('/allocate_multiple_course_seats', methods=['POST'])
def allocate_multiple_course_seats():
    first_course_name = request.form['First_Course_name']
    number_of_students_first = int(request.form['Number_of_Students_First'])
    starting_reg_number_first = request.form['Starting_Reg_Number_First']
    classroom_number_first = request.form['Classroom_Number_First']

    second_course_name = request.form['Second_Course_name']
    number_of_students_second = int(request.form['Number_of_Students_Second'])
    starting_reg_number_second = request.form['Starting_Reg_Number_Second']
    classroom_number_second = request.form['Classroom_Number_Second']

    try:
        with connect_db() as db:
            cursor = db.cursor()
            updated_count = 0  # Counter for updates
            new_count = 0  # Counter for new allocations

            # Allocate or update seats for the first course
            cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no = %s", (classroom_number_first,))
            number_of_seats_first = cursor.fetchone()[0]

            if number_of_students_first > number_of_seats_first // 2:
                flash('Number of students exceeds the number of available seats for the first course.')
                return redirect(url_for('allot_examination_seats'))

            for i in range(number_of_students_first):
                reg_suffix = str(int(starting_reg_number_first[-3:]) + i).zfill(len(starting_reg_number_first[-3:]))
                new_reg_number_first = starting_reg_number_first[:-3] + reg_suffix
                seat_number = (i * 2) + 1  # Allocating seats 1, 3, 5...

                # Check if a seat allocation already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM seat_allocation WHERE Reg_number = %s AND Classroom_number = %s
                """, (new_reg_number_first, classroom_number_first))
                exists = cursor.fetchone()[0]

                if exists:
                    # Update existing seat allocation
                    cursor.execute("""
                        UPDATE seat_allocation SET Seat_number = %s WHERE Reg_number = %s AND Classroom_number = %s
                    """, (seat_number, new_reg_number_first, classroom_number_first))
                    updated_count += 1
                else:
                    # Insert new seat allocation
                    cursor.execute("""
                        INSERT INTO seat_allocation (Reg_number, Classroom_number, Seat_number) 
                        VALUES (%s, %s, %s)
                    """, (new_reg_number_first, classroom_number_first, seat_number))
                    new_count += 1

            # Allocate or update seats for the second course
            cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no = %s", (classroom_number_second,))
            number_of_seats_second = cursor.fetchone()[0]

            if number_of_students_second > number_of_seats_second // 2:
                flash('Number of students exceeds the number of available seats for the second course.')
                return redirect(url_for('allot_examination_seats'))

            for i in range(number_of_students_second):
                reg_suffix = str(int(starting_reg_number_second[-3:]) + i).zfill(len(starting_reg_number_second[-3:]))
                new_reg_number_second = starting_reg_number_second[:-3] + reg_suffix
                seat_number = (i * 2) + 2  # Allocating seats 2, 4, 6...

                # Check if a seat allocation already exists
                cursor.execute("""
                    SELECT COUNT(*) FROM seat_allocation WHERE Reg_number = %s AND Classroom_number = %s
                """, (new_reg_number_second, classroom_number_second))
                exists = cursor.fetchone()[0]

                if exists:
                    # Update existing seat allocation
                    cursor.execute("""
                        UPDATE seat_allocation SET Seat_number = %s WHERE Reg_number = %s AND Classroom_number = %s
                    """, (seat_number, new_reg_number_second, classroom_number_second))
                    updated_count += 1
                else:
                    # Insert new seat allocation
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