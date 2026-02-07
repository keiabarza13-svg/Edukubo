from flask import Flask, jsonify
from database import get_connection # Imports your database connection

app = Flask(__name__)

# --- 1. Homepage Route (To check if it works) ---
@app.route('/')
def home():
    return "<h1>EduKubo Server is Online! 🚀</h1><p>Ready to connect with ESP32.</p>"

# --- 2. Database Test Route ---
@app.route('/api/test-db')
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "success", "message": "Database connected successfully!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    # '0.0.0.0' allows the ESP32 to find this server on the network
    app.run(host='0.0.0.0', port=5000, debug=True)