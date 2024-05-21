from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('job_portal.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return 'Hello, World! '


#apiendppoints you would need postman or curl for this
@app.route('/apply', methods=['POST'])
def apply_to_job():
    user_id = request.json['user_id']
    job_id = request.json['job_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO Applications (user_id, job_id, application_date) VALUES (?, ?, ?)"
    cursor.execute(query, (user_id, job_id, datetime.now()))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Application submitted successfully!"})

@app.route('/user_applications/<int:user_id>', methods=['GET'])
def get_user_applications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM Applications WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    
    applications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify([dict(row) for row in applications])

if __name__ == '__main__':
    app.run(debug=True)
