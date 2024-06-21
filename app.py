from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('job_portal.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM JobPostings"
    cursor.execute(query)
    
    jobs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('index.html', jobs=jobs)

@app.route('/apply', methods=['POST'])
def apply_to_job():
    user_id = request.form['user_id']
    job_id = request.form['job_id']
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "INSERT INTO Applications (user_id, job_id, application_date) VALUES (?, ?, ?)"
    cursor.execute(query, (user_id, job_id, datetime.now()))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))

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
