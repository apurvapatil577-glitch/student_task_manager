import mysql.connector

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root@1234',
            database='student_task_manager'
        )
        return connection
    except mysql.connector.Error as err:
        print("Database Error:", err)
        return None 