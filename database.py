import sqlite3

def init_db():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Create student table
    cursor.execute('''CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        reg_no TEXT UNIQUE,
                        branch TEXT,
                        topic1 TEXT,
                        topic2 TEXT,
                        topic3 TEXT,
                        password TEXT)''')

    # Create file storage table
    cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_reg_no TEXT,
                        filename TEXT,
                        FOREIGN KEY(student_reg_no) REFERENCES students(reg_no))''')

    conn.commit()
    conn.close()

# Run this when starting the application
init_db()
