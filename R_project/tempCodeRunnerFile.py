@app.route('/seat_allocation')
def seat_allocation():
    reg_number = session.get('rn')

    conn = get_db_connection()
    if conn is None:
        flash('Database connection failed!', 'danger')
        return redirect('/')

    cursor = conn.cursor()

    try:
        # Check for seat allocation for the student
        cursor.execute("SELECT * FROM seat_allocation WHERE Reg_number=%s", (reg_number,))
        seat_details = cursor.fetchone()

        if not seat_details:
            return render_template('seat_allocation.html', allocation_exists=False, rows=3)

        classroom_number = seat_details[1]
        seat_number = seat_details[2]

        # Retrieve the total number of seats from classroom_size
        cursor.execute("SELECT number_of_seats FROM classroom_size WHERE no=%s", (classroom_number,))
        classroom_data = cursor.fetchone()

        if classroom_data:
            total_seats = classroom_data[0]
        else:
            flash('Classroom not found.', 'danger')
            return redirect('/')

        # Fetch all seat allocations for the specific classroom
        cursor.execute("SELECT * FROM seat_allocation WHERE Classroom_number=%s ORDER BY seat_number", (classroom_number,))
        seat_allocations = cursor.fetchall()

        # Prepare seat allocation layout with room and seat numbers
        seat_allocation = ['x'] * total_seats
        for allocation in seat_allocations:
            seat_allocation[allocation[2] - 1] = allocation[0]  # Place registration number in correct seat

        rows = 3  # Set number of rows

        return render_template(
            'seat_allocation.html', 
            allocation_exists=True, 
            reg_number=reg_number, 
            total_seats=total_seats, 
            seat_allocation=seat_allocation, 
            rows=rows, 
            seat_number=seat_number,
            classroom_number=classroom_number  # Pass the classroom number to the template
        )
    
    except Error as e:
        flash(f'Error fetching seat allocation: {e}', 'danger')
        return redirect('/')

    finally:
        cursor.close()
        conn.close()