import math
from server_rpi.database import get_connection

# BKT (Question/Skill-Level Mastery)

def create_skill_mastery(student_id: int, skill_id: int):
    """
    Initialize skill mastery for a student.
    Default = 0.2 (20% chance student knows skill)
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO student_skill_mastery
        (student_id, skill_id, mastery_probability)
        VALUES (?, ?, 0.2)
    """, (student_id, skill_id))
    conn.commit()
    conn.close()


def get_mastery(student_id: int, skill_id: int):
    """Get current mastery probability for a skill"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mastery_probability FROM student_skill_mastery
        WHERE student_id = ? AND skill_id = ?
    """, (student_id, skill_id))
    row = cursor.fetchone()
    conn.close()
    return row["mastery_probability"] if row else 0.2


def bkt_update(student_id: int, skill_id: int, correct: int,
               slip=0.1, guess=0.2, learn=0.15):
    """
    Update skill mastery using BKT
    - correct: 1 if answered correctly, 0 if wrong
    - slip: chance student knows skill but answers wrong
    - guess: chance student guesses correctly
    - learn: learning rate (how much mastery increases per question)
    """
    conn = get_connection()
    cursor = conn.cursor()

    # get current mastery
    cursor.execute("""
        SELECT mastery_probability FROM student_skill_mastery
        WHERE student_id = ? AND skill_id = ?
    """, (student_id, skill_id))
    row = cursor.fetchone()
    L_t = row["mastery_probability"] if row else 0.2

    # Bayesian update
    if correct:
        L_t_new = (L_t * (1 - slip)) / (L_t * (1 - slip) + (1 - L_t) * guess)
    else:
        L_t_new = (L_t * slip) / (L_t * slip + (1 - L_t) * (1 - guess))

    # Apply learning transition
    L_t_new = L_t_new + (1 - L_t_new) * learn

    # Save updated mastery
    if row:
        cursor.execute("""
            UPDATE student_skill_mastery
            SET mastery_probability = ?
            WHERE student_id = ? AND skill_id = ?
        """, (L_t_new, student_id, skill_id))
    else:
        cursor.execute("""
            INSERT INTO student_skill_mastery
            (student_id, skill_id, mastery_probability)
            VALUES (?, ?, ?)
        """, (student_id, skill_id, L_t_new))

    conn.commit()
    conn.close()
    return L_t_new
