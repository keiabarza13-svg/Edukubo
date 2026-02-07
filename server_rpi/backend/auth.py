from backend.database import get_connection
from backend.student_model import create_student_model
import bcrypt

# ---------------------------------------------
# This is where we handle registration and login for Edukubo.
# I made sure that when a student registers, we also create
# their student_model so our adaptive system knows they are new.
# ---------------------------------------------

# ------------------------
# Register a new student
# ------------------------
def register_student(full_name: str, username: str, password: str, grade_level: int):
    """
    When a new student signs up:
    1. I hash their password for security
    2. Insert them into the users table as a student
    3. Add their grade level to the students table
    4. Create a student_model row with ability=0 and mastery=0
       - This ensures the first story is the deciding story
       - The system can start learning from their first quiz
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Hash the password before saving it
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        # Insert student into users table
        cursor.execute("""
            INSERT INTO users (full_name, username, password_hash, role)
            VALUES (?, ?, ?, 'student')
        """, (full_name, username, password_hash))
        user_id = cursor.lastrowid

        # Insert into students table with grade level
        cursor.execute("""
            INSERT INTO students (student_id, grade_level)
            VALUES (?, ?)
        """, (user_id, grade_level))

        # Create the student_model for adaptive learning
        create_student_model(user_id, ability=0.0, mastery=0.0)

        conn.commit()
        conn.close()
        return {"success": True, "message": "Student registered successfully.", "user_id": user_id}

    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}


# ------------------------
# Register a new teacher
# ------------------------
def register_teacher(full_name: str, username: str, password: str):
    """
    When a teacher registers:
    1. I hash their password for security
    2. Insert them into the users table as a teacher
    3. Teachers don't need a student_model
    """
    conn = get_connection()
    cursor = conn.cursor()

    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        cursor.execute("""
            INSERT INTO users (full_name, username, password_hash, role)
            VALUES (?, ?, ?, 'teacher')
        """, (full_name, username, password_hash))
        user_id = cursor.lastrowid

        conn.commit()
        conn.close()
        return {"success": True, "message": "Teacher registered successfully.", "user_id": user_id}

    except Exception as e:
        conn.close()
        return {"success": False, "message": str(e)}


# ------------------------
# Login for both students and teachers
# ------------------------
def login(username: str, password: str):
    """
    When someone logs in:
    1. I check the users table for the username
    2. If it exists, I verify the password
    3. Return user info and role if login is successful
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return {"success": False, "message": "User not found"}

    # Check hashed password
    if bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        return {
            "success": True,
            "message": "Login successful",
            "user_id": user["user_id"],
            "role": user["role"],
            "full_name": user["full_name"]
        }
    else:
        return {"success": False, "message": "Incorrect password"}


