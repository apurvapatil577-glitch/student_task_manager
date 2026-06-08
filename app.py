from flask import Flask, render_template, request, redirect, url_for, session
from db_config import get_db_connection

app = Flask(__name__)
app.secret_key = "student_task_manager_secret_key"

# ==========================
# HOME -> LOGIN PAGE
# ==========================
@app.route('/')
def home():
    return redirect(url_for('login'))


# ==========================
# LOGIN
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":

            session['user'] = username

            return redirect(url_for('dashboard'))

        return "Invalid Username or Password"

    return render_template('login.html')

# ==========================
# DASHBOARD
# ==========================
@app.route('/dashboard')
def dashboard():

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    student_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    attendance_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM student_tasks")
    assignment_count = cursor.fetchone()[0]

    cursor.close()
    connection.close()

    return render_template(
        'index.html',
        student_count=student_count,
        task_count=task_count,
        attendance_count=attendance_count,
        assignment_count=assignment_count
    )


# ==========================
# ADD STUDENT
# ==========================
@app.route('/add_student', methods=['GET', 'POST'])
def add_students():

    if request.method == 'POST':

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        mobile_number = request.form['mobile_number']
        email = request.form['email']
        course_name = request.form['course_name']
        admission_date = request.form['admission_date']

        connection = get_db_connection()
        cursor = connection.cursor()

        query = """
        INSERT INTO students
        (
            first_name,
            last_name,
            gender,
            mobile_number,
            email,
            course_name,
            admission_date
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s)
        """

        cursor.execute(query, (
            first_name,
            last_name,
            gender,
            mobile_number,
            email,
            course_name,
            admission_date
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('students'))

    return render_template('add_student.html')


# ==========================
# STUDENTS LIST
# ==========================
@app.route('/students')
def students():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'students.html',
        students=students
    )


# ==========================
# EDIT STUDENT
# ==========================
@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':

        cursor.execute("""
        UPDATE students
        SET
            first_name=%s,
            last_name=%s,
            gender=%s,
            mobile_number=%s,
            email=%s,
            course_name=%s
        WHERE student_id=%s
        """, (
            request.form['first_name'],
            request.form['last_name'],
            request.form['gender'],
            request.form['mobile_number'],
            request.form['email'],
            request.form['course_name'],
            student_id
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('students'))

    cursor.execute(
        "SELECT * FROM students WHERE student_id=%s",
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template(
        'edit_student.html',
        student=student
    )


# ==========================
# DELETE STUDENT
# ==========================
@app.route('/delete_student/<int:student_id>')
def delete_student(student_id):

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute(
        "DELETE FROM students WHERE student_id=%s",
        (student_id,)
    )

    connection.commit()

    cursor.close()
    connection.close()

    return redirect(url_for('students'))


# ==========================
# TASKS LIST
# ==========================
@app.route('/tasks')
def tasks():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'tasks.html',
        tasks=tasks
    )


# ==========================
# ADD TASK
# ==========================
@app.route('/add_task', methods=['GET', 'POST'])
def add_task():

    if request.method == 'POST':

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
        INSERT INTO tasks
        (
            task_name,
            description,
            due_date
        )
        VALUES (%s,%s,%s)
        """, (
            request.form['task_name'],
            request.form['description'],
            request.form['due_date']
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('tasks'))

    return render_template('add_task.html')


# ==========================
# ASSIGN TASK
# ==========================
@app.route('/assign_task', methods=['GET', 'POST'])
def assign_task():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':

        cursor.execute("""
        INSERT INTO student_tasks
        (
            student_id,
            task_id
        )
        VALUES (%s,%s)
        """, (
            request.form['student_id'],
            request.form['task_id']
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('student_tasks'))

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'assign_task.html',
        students=students,
        tasks=tasks
    )


# ==========================
# STUDENT TASKS
# ==========================
@app.route('/student_tasks')
def student_tasks():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        st.id,
        s.first_name,
        s.last_name,
        t.task_name,
        t.description,
        t.due_date
    FROM student_tasks st
    JOIN students s
    ON st.student_id=s.student_id
    JOIN tasks t
    ON st.task_id=t.task_id
    """)

    student_tasks = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'student_tasks.html',
        student_tasks=student_tasks
    )


# ==========================
# ATTENDANCE
# ==========================
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':

        cursor.execute("""
        INSERT INTO attendance
        (
            student_id,
            attendance_date,
            status
        )
        VALUES (%s,%s,%s)
        """, (
            request.form['student_id'],
            request.form['attendance_date'],
            request.form['status']
        ))

        connection.commit()

        cursor.close()
        connection.close()

        return redirect(url_for('attendance_report'))

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'attendance.html',
        students=students
    )


# ==========================
# ATTENDANCE REPORT
# ==========================
@app.route('/attendance_report')
def attendance_report():

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
    SELECT
        a.attendance_id,
        s.first_name,
        s.last_name,
        a.attendance_date,
        a.status
    FROM attendance a
    JOIN students s
    ON a.student_id=s.student_id
    ORDER BY a.attendance_date DESC
    """)

    attendance_records = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template(
        'attendance_report.html',
        attendance_records=attendance_records
    )

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ==========================
# RUN APP
# ==========================
if __name__ == '__main__':
    app.run(debug=True)