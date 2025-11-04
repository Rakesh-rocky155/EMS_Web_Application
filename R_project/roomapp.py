from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flashing messages

# Database connection setup
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),  # Set your password
            database=os.getenv('DB_NAME', 'exam_management'),  # Set your database name
            port=int(os.getenv('DB_PORT', 3306))  # Default port
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

# Route for allocating a room
@app.route('/allocate_room', methods=['GET', 'POST'])
def allocate_room():
    if request.method == 'POST':
        # Retrieve form data
        classroom_no = request.form.get('classroom_no')
        capacity = request.form.get('capacity')

        # Validate form data
        if not classroom_no or not capacity:
            flash("Please fill in all the fields!", 'error')
            return redirect(url_for('handle_allocate_room'))

        try:
            conn = get_db_connection()
            if conn is None:
                flash("Database connection error!", 'error')
                return redirect(url_for('handle_allocate_room'))

            cursor = conn.cursor()

            # Check if the classroom already exists
            check_sql = '''
                SELECT * FROM classroom_size 
                WHERE no = %s
            '''
            cursor.execute(check_sql, (classroom_no,))
            existing_record = cursor.fetchone()

            if existing_record:
                # Update the room capacity if it exists
                update_sql = '''
                    UPDATE classroom_size
                    SET number_of_seats = %s
                    WHERE no = %s
                '''
                cursor.execute(update_sql, (capacity, classroom_no))
                flash(f"Classroom {classroom_no} updated successfully!", 'success')
            else:
                # Insert new record
                insert_sql = '''
                    INSERT INTO classroom_size (no, number_of_seats)
                    VALUES (%s, %s)
                '''
                cursor.execute(insert_sql, (classroom_no, capacity))
                flash(f"Classroom {classroom_no} added successfully!", 'success')

            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            flash(f"Error: {err}", 'error')

    return render_template('allocate_room.html')

# Route for viewing room allocations
@app.route('/view_room_allocation', methods=['GET'])
def view_room_allocation():
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('allocate_room'))

        cursor = conn.cursor()
        cursor.execute('SELECT no, number_of_seats FROM classroom_size')
        allocations = cursor.fetchall()
        cursor.close()
        conn.close()

        # Check if allocations list is empty
        if not allocations:
            flash("No rooms have been allocated yet!", 'info')

        return render_template('view_room_allocation.html', allocations=allocations)
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')
        return redirect(url_for('allocate_room'))


# Route for clearing a specific room allocation
@app.route('/clear_room_allocation', methods=['POST'])
def clear_room_allocation():
    classroom_no = request.form.get('classroom_no')

    if not classroom_no:
        flash("Please specify a classroom number!", 'error')
        return redirect(url_for('view_room_allocation'))

    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('display_allocate_room'))

        cursor = conn.cursor()
        cursor.execute('DELETE FROM classroom_size WHERE no = %s', (classroom_no,))
        conn.commit()
        cursor.close()
        conn.close()

        flash(f"Classroom {classroom_no} deleted successfully!", 'success')
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('display_allocate_room'))

# Route for clearing all room allocations
@app.route('/clear_all_records', methods=['POST'])
def clear_all_records():
    try:
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error!", 'error')
            return redirect(url_for('display_allocate_room'))

        cursor = conn.cursor()
        cursor.execute('DELETE FROM classroom_size')
        conn.commit()
        cursor.close()
        conn.close()

        flash("All room allocations cleared successfully!", 'success')
    except mysql.connector.Error as err:
        flash(f"Error: {err}", 'error')

    return redirect(url_for('display_allocate_room'))

if __name__ == '__main__':
    app.run(debug=True)
