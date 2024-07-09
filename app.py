from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import sqlite3
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
app.secret_key = 'your_secret_key' 
CORS(app, resources={r"/*": {"origins": "*"}})

app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7) 


def get_db_connection():
    conn = sqlite3.connect('job_portal.db')
    conn.row_factory = sqlite3.Row
    return conn



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    print("Received registration data:", data)  # Log received data
    name = data['name']
    email = data['email']
    password = data['password']
    user_type = data['user_type']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO Users (name, email, password, user_type) 
            VALUES (?, ?, ?, ?)
        ''', (name, email, password, user_type))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/login', methods=['POST'])
#just get password 
def login():
    data = request.get_json()
    email = data['email']
    password = data['password']

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT password FROM Users WHERE email = ?', (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if  user['password'] == password:  
        session.permanent = True
        session['user_id'] = user['user_id']
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'error': 'Invalid email or password'}), 401

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200


@app.route('/apply', methods=['POST'])
def apply_to_job():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = session['user_id']
    job_id = data['job_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO Applications (applicant_id, job_posting_id, application_date, status) VALUES (?, ?, ?, 'Applied')"
        cursor.execute(query, (user_id, job_id, datetime.now()))
        conn.commit()
        return jsonify({'message': 'Application submitted successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'You have already applied for this job'}), 400
    finally:
        cursor.close()
        conn.close()



@app.route('/check_auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        return jsonify({'authenticated': True, 'user_id': session['user_id']}), 200
    else:
        return jsonify({'authenticated': False}), 401

@app.route('/delete_application/<int:job_id>', methods=['DELETE'])
def delete_application(job_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM Applications WHERE applicant_id = ? AND job_posting_id = ?"
        cursor.execute(query, (user_id, job_id))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Application deleted successfully'}), 200
        else:
            return jsonify({'error': 'Application not found'}), 404
    finally:
        cursor.close()
        conn.close()

@app.route('/user_applications/<int:user_id>', methods=['GET'])
def get_user_applications(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM Applications WHERE applicant_id = ?"
    cursor.execute(query, (user_id,))
    
    applications = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify([dict(row) for row in applications])


@app.route('/jobs', methods=['GET'])
def get_jobs():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM JobPostings"
    cursor.execute(query)
    
    jobs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify([dict(row) for row in jobs])


@app.route('/search_jobs', methods=['GET'])
def search_jobs():
    query = request.args.get('query', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    search_query = f"""
    SELECT * FROM JobPostings 
    WHERE business_title LIKE '%{query}%' 
    OR agency LIKE '%{query}%'
    """
    
    cursor.execute(search_query)
    jobs = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify({'jobs': [dict(row) for row in jobs]})


@app.route('/save_job', methods=['POST'])
def save_job():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.get_json()
    user_id = session['user_id']
    job_id = data['job_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "INSERT INTO SavedJobPostings (ApplicantID, JobPostingID) VALUES (?, ?)"
        cursor.execute(query, (user_id, job_id))
        conn.commit()
        return jsonify({'message': 'Job saved successfully'}), 201
    except sqlite3.IntegrityError:
        return jsonify({'error': 'You have already saved this job'}), 400
    finally:
        cursor.close()
        conn.close()

@app.route('/unsave_job/<int:job_id>', methods=['DELETE'])
def unsave_job(job_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        query = "DELETE FROM SavedJobPostings WHERE ApplicantID = ? AND JobPostingID = ?"
        cursor.execute(query, (user_id, job_id))
        conn.commit()
        if cursor.rowcount > 0:
            return jsonify({'message': 'Job unsaved successfully'}), 200
        else:
            return jsonify({'error': 'Saved job not found'}), 404
    finally:
        cursor.close()
        conn.close()

@app.route('/saved_jobs', methods=['GET'])
def get_saved_jobs():
    #if 'user_id' not in session:
    #    return jsonify({'error': 'Unauthorized'}), 401

    #user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT jp.*
    FROM JobPostings jp
    JOIN SavedJobPostings sjp ON jp.job_id = sjp.JobPostingID
    WHERE sjp.ApplicantID = 2
    """
    cursor.execute(query)
    saved_jobs = cursor.fetchall()


    cursor.close()
    conn.close()

    # Convert sqlite3.Row objects to dictionaries
    saved_jobs_list = []
    for row in saved_jobs:
        job_dict = {}
        for key in row.keys():
            job_dict[key] = row[key]
        saved_jobs_list.append(job_dict)

    print("Saved jobs:", saved_jobs_list)  # Debug print
    return jsonify(saved_jobs_list)

if __name__ == '__main__':
    app.run(debug=True)
