from flask import Flask, render_template, abort
from database import get_connection 

app = Flask(__name__)

# --- ROUTE 1: The Dashboard (List all stories) ---
@app.route('/')
def home():
    conn = get_connection()
    # fetchall() gives us a list of all rows in the 'stories' table
    stories = conn.execute('SELECT * FROM stories').fetchall()
    conn.close()
    return render_template('index.html', stories=stories)

# --- ROUTE 2: Read a Specific Story ---
@app.route('/story/<int:story_id>')
def view_story(story_id):
    conn = get_connection()
    # We fetch just ONE row where the ID matches
    story = conn.execute('SELECT * FROM stories WHERE story_id = ?', (story_id,)).fetchone()
    conn.close()

    if story is None:
        return abort(404) # Show error if ID doesn't exist

    return render_template('story.html', story=story)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)