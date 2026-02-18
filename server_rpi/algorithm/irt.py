import math
from server_rpi.database import get_connection

def create_student_model(student_id: int):
    """
    When a student registers:
    - Initialize story-level ability (θ) to 0
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO student_model (student_id, ability, mastery)
        VALUES (?, 0.0, 0.0)
    """, (student_id,))
    conn.commit()
    conn.close()



# IRT (Story-Level Ability)

def get_ability(student_id: int):
    """Get current story-level ability θ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ability FROM student_model WHERE student_id = ?
    """, (student_id,))
    row = cursor.fetchone()
    conn.close()
    return row["ability"] if row else 0.0


def update_ability(student_id: int, theta: float):
    """Update story-level ability θ"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE student_model SET ability = ? WHERE student_id = ?
    """, (theta, student_id))
    conn.commit()
    conn.close()


def irt_update(student_id: int, story_difficulty: float, responses: list):
    """
    Update ability θ using Rasch IRT.
    - story_difficulty: difficulty (b) of story
    - responses: list of 1s (correct) and 0s (incorrect)
    """
    theta = get_ability(student_id)
    learning_rate = 0.1

    for actual in responses:
        p = 1 / (1 + math.exp(-(theta - story_difficulty)))  # Rasch probability
        theta = theta + learning_rate * (actual - p)  # gradient update

    update_ability(student_id, theta)
    return theta


