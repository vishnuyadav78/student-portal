from pywebio.input import input, input_group, TEXT, PASSWORD, file_upload
from pywebio.output import put_text, put_success, put_error
from pywebio.platform.flask import start_server
import sqlite3
import os

UPLOAD_FOLDER = "files/"

# Initialize database
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
                        topic3 TEXT)''')

    # Create file storage table
    cursor.execute('''CREATE TABLE IF NOT EXISTS files (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_reg_no TEXT,
                        filename TEXT,
                        FOREIGN KEY(student_reg_no) REFERENCES students(reg_no))''')

    conn.commit()
    conn.close()

init_db()

# Student Registration
def register_student():
    student_data = input_group("Student Registration", [
        input("Full Name", name="name", type=TEXT),
        input("Registration Number", name="reg_no", type=TEXT),
        input("Branch", name="branch", type=TEXT),
        input("Topic 1", name="topic1", type=TEXT),
        input("Topic 2", name="topic2", type=TEXT),
        input("Topic 3", name="topic3", type=TEXT)
    ])

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO students (name, reg_no, branch, topic1, topic2, topic3) VALUES (?, ?, ?, ?, ?, ?)",
                       (student_data["name"], student_data["reg_no"], student_data["branch"], student_data["topic1"], student_data["topic2"], student_data["topic3"]))
        conn.commit()
        put_success("Registration Successful! Use your Name as Username and Reg No as Password to log in.")
    except sqlite3.IntegrityError:
        put_error("Registration Number already exists!")

    conn.close()

# Login Page
def login():
    login_data = input_group("Login", [
        input("Full Name", name="name", type=TEXT),
        input("Registration Number", name="reg_no", type=PASSWORD)
    ])

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE name = ? AND reg_no = ?", (login_data["name"], login_data["reg_no"]))
    student = cursor.fetchone()

    if student:
        put_success(f"Welcome {student[1]}! You can now upload or delete your files.")
        student_dashboard(login_data["reg_no"])
    elif login_data["name"] == "admin" and login_data["reg_no"] == "admin123":
        put_success("Welcome, Admin! You can manage all student files.")
        admin_dashboard()
    else:
        put_error("Invalid login credentials!")

    conn.close()

# Student Dashboard - File Upload
def student_dashboard(reg_no):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    uploaded_file = file_upload("Upload your file", accept="*/*")
    if uploaded_file:
        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file["filename"])
        with open(filepath, "wb") as f:
            f.write(uploaded_file["content"])

        conn = sqlite3.connect("students.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO files (student_reg_no, filename) VALUES (?, ?)", (reg_no, uploaded_file["filename"]))
        conn.commit()
        conn.close()
        put_success("File uploaded successfully!")

# Admin Dashboard - View All Files
def admin_dashboard():
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM files")
    files = cursor.fetchall()
    conn.close()

    put_text("All Student Files:")
    for file in files:
        put_text(f"Student: {file[1]}, File: {file[2]}")

# Run the application
if __name__ == "__main__":
    start_server([register_student, login], port=8080, debug=True)
