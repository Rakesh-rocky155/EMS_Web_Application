import mysql.connector
from config import Config

def get_db_connection():
    connection = mysql.connector.connect(
        host=Config.MYSQL_HOST,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DB
    )
    return connection

def create_marks_sheet():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks_sheet (
            Reg_number VARCHAR(20),
            Subject VARCHAR(20),
            IA1 INT DEFAULT 0,
            IA2 INT DEFAULT 0,
            Final INT DEFAULT 0
        )
    """)
    connection.commit()
    cursor.close()
    connection.close()

def drop_marks_sheet():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS marks_sheet")
    connection.commit()
    cursor.close()
    connection.close()
