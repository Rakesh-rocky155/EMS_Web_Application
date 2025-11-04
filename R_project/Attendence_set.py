from flask import Flask, request, redirect, url_for, session, render_template_string
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def db_connection():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="exam_management"
        )
        return con
    except Error as e:
        print(f"Error: {e}")
        return None

@app.route('/attendence_set', methods=['POST'])
def attendence_set():
    rn = request.form['rn']
    ac = request.form['ac']
    tc = request.form['tc']
    
    session['rn'] = rn
    session['ac'] = ac
    session['tc'] = tc

    con = db_connection()
    
    if con:
        cursor = con.cursor()
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        verify = False
        for table in tables:
            if table[0] == "attendance":
                verify = True

        if not verify:
            # Create the attendance table if not exists
            create_table_query = """
            CREATE TABLE attendance(
                Reg_number VARCHAR(20),
                Attended_classes INT(20),
                Total_Classes INT(20)
            )
            """
            cursor.execute(create_table_query)
            con.commit()

        # Check if the record for the given Reg_number exists
        query = "SELECT * FROM attendance WHERE Reg_number = %s"
        cursor.execute(query, (rn,))
        result = cursor.fetchall()

        if result:
            # Record exists, ask for update confirmation
            return render_template_string("""
                <script>
                    function verify() {
                        c = confirm('There is already a value present. Do you want to update it?');
                        if (c) {
                            window.location.replace('{{ url_for('attendence_update') }}');
                        } else {
                            alert('Values not added');
                            window.location.replace('{{ url_for('attendence_set_form') }}');
                        }
                    }
                    verify();
                </script>
            """)
        else:
            # Insert new record if no existing record is found
            insert_query = "INSERT INTO attendance (Reg_number, Attended_classes, Total_Classes) VALUES (%s, %s, %s)"
            cursor.execute(insert_query, (rn, ac, tc))
            con.commit()
            
            if cursor.rowcount > 0:
                return "<script>alert('Attendance Added'); window.location.replace('/attendence_set_form');</script>"
    
    else:
        return "<script>alert('Database is not connected');</script>"

    return redirect(url_for('attendence_set_form'))

@app.route('/attendence_update')
def attendence_update():
    # Logic for updating attendance (you can fill this with actual update logic)
    return "Attendance update page placeholder."

@app.route('/attendence_set_form')
def attendence_set_form():
    # Placeholder form page (can be replaced with HTML template or actual form page)
    return '''
    <form action="/attendence_set" method="POST">
        <label>Register Number:</label><input type="text" name="rn"><br>
        <label>Attended Classes:</label><input type="number" name="ac"><br>
        <label>Total Classes:</label><input type="number" name="tc"><br>
        <input type="submit" value="Submit">
    </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
