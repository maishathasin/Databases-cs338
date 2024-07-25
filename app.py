from flask import Flask, request, jsonify, redirect, url_for, session,make_response
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import sqlite3
from datetime import datetime, timedelta
from flask_cors import CORS
import json
import logging


app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app, supports_credentials=True, origins=['http://localhost:5173'])

app.config['SECRET_KEY'] = 'your_very_secret_key_here'  # Change this!
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)
app.config['REMEMBER_COOKIE_HTTPONLY'] = True
app.config['REMEMBER_COOKIE_SECURE'] = False  # Set to True in production with HTTPS

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"



@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
    print(f"Before request - Session: {session}")
    print(f"Before request - Current user: {current_user}")

class User(UserMixin):
    def __init__(self, user_id, name, email, user_type):
        self.id = user_id
        self.name = name
        self.email = email
        self.user_type = user_type

    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(user['user_id'], user['name'], user['email'], user['user_type'])
    return None

def get_db_connection():
    conn = sqlite3.connect('job_portal.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data['name']
    email = data['email']
    password = data['password']
    user_type = data['user_type']

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO Users (name, email, password, user_type) VALUES (?, ?, ?, ?)', (name, email, password, user_type))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already exists'}), 400
    finally:
        cursor.close()
        conn.close()

    return jsonify({'message': 'User registered successfully'}), 201



# change login, if the user is an employer or not 
@app.route('/login', methods=['GET', 'POST'])
def login():  
    print("Login route accessed")
    if request.method == 'POST':
        data = request.get_json()
        email = data['email']
        password = data['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE email = ?', (email,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and user['password'] == password:
            user_id = user['user_id']
            login_user(User(user['user_id'], user['name'], user['email'], user['user_type']))
            
            return jsonify({
                'message': 'Login successful',
                'success': True,
                'user_id': user_id,
                'name': user['name'],
                'email': user['email'],
                'user_type': user['user_type'],
                'authenticated': True,
                'redirect': '/jobs'
            }), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    elif request.method == 'GET':
        return jsonify({"message": "Please log in"}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    session.pop('user_id', None)
    return jsonify({'message': 'Logged out successfully'}), 200

from flask import request, jsonify
import sqlite3

@app.route('/get_saved_jobs', methods=['GET'])
def get_saved_jobs():
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT j.job_id, j.business_title, j.agency, j.work_location
            FROM SavedJobPostings s
            JOIN JobPostings j ON s.JobPostingID = j.job_id
            WHERE s.ApplicantID = ?
        ''', (user_id,))
        saved_jobs = cursor.fetchall()
        
        # Convert the result to a list of dictionaries
        saved_jobs_list = [
            {
                "job_id": job[0],
                "business_title": job[1],
                "agency": job[2],
                "work_location": job[3]
            } for job in saved_jobs
        ]
        
        return jsonify({"savedJobs": saved_jobs_list}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()



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
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    data = request.get_json()
    job_id = data.get('job_id')

    if not job_id:
        return jsonify({"error": "Job ID not provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the job is already saved
        cursor.execute("SELECT * FROM SavedJobPostings WHERE ApplicantID = ? AND JobPostingID = ?", (user_id, job_id))
        existing_save = cursor.fetchone()
        
        if existing_save:
            return jsonify({"message": "Job already saved"}), 200

        # Save the job
        cursor.execute("INSERT INTO SavedJobPostings (ApplicantID, JobPostingID) VALUES (?, ?)", (user_id, job_id))
        conn.commit()
        
        return jsonify({"message": "Job saved successfully"}), 201
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/unsave_job/<int:job_id>', methods=['DELETE'])
def unsave_job(job_id):
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the saved job exists
        cursor.execute("SELECT * FROM SavedJobPostings WHERE ApplicantID = ? AND JobPostingID = ?", (user_id, job_id))
        saved_job = cursor.fetchone()
        
        if not saved_job:
            return jsonify({"error": "Saved job not found"}), 404

        # Delete the saved job
        cursor.execute("DELETE FROM SavedJobPostings WHERE ApplicantID = ? AND JobPostingID = ?", (user_id, job_id))
        conn.commit()
        
        return jsonify({"message": "Job unsaved successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()



@app.route('/api/user', methods=['GET'])
def get_user_data():
    # Assuming you have some way to identify the current user, e.g., session
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, name, email, user_type FROM Users WHERE user_id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        return jsonify({
            'user_id': user['user_id'],
            'name': user['name'],
            'email': user['email'],
            'user_type': user['user_type']
        }), 200
    else:
        return jsonify({'error': 'User not found'}), 404
    

logging.basicConfig(level=logging.DEBUG)
import traceback

@app.route('/job_recommendations', methods=['GET'])
def get_job_recommendations():
    try:
        user_id = request.headers.get('User-Id')
        print("Receive")
        logging.debug(f"Received request for job recommendations for user_id: {user_id}")
        
        if not user_id:
            logging.warning("User ID not provided in request headers")
            return jsonify({"error": "User ID not provided"}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if the user has any applications
        cursor.execute('SELECT COUNT(*) FROM Applications WHERE applicant_id = ?', (user_id,))
        application_count = cursor.fetchone()[0]
        logging.debug(f"User {user_id} has {application_count} applications")

        if application_count == 0:
            logging.debug(f"No application history found for user {user_id}")
            # If no applications, we'll use a default set of skills or get all jobs
            user_skills = []
        else:
            # Fetch skills from the most recent application
            cursor.execute('''
                SELECT jp.preferred_skills
                FROM Applications a
                JOIN JobPostings jp ON a.job_posting_id = jp.job_id
                WHERE a.applicant_id = ?
                ORDER BY a.application_date DESC
                LIMIT 1
            ''', (user_id,))
            user_skills_row = cursor.fetchone()
            user_skills = user_skills_row['preferred_skills'].split(',') if user_skills_row else []

        logging.debug(f"User skills: {user_skills}")

        # Modify the query to get all jobs if no skills are found
        if user_skills:
            user_skills_str = ','.join(user_skills)
            query = '''
                SELECT 
                    jp.job_id,
                    jp.business_title,
                    jp.agency,
                    jp.work_location,
                    jp.salary_range_from,
                    jp.salary_range_to,
                    CASE 
                        WHEN a.job_posting_id IS NULL THEN 1
                        ELSE 0
                    END as not_applied,
                    (LENGTH(jp.job_description) - LENGTH(REPLACE(LOWER(jp.job_description), LOWER(?), ''))) / LENGTH(?) as description_match_score,
                    (LENGTH(jp.preferred_skills) - LENGTH(REPLACE(LOWER(jp.preferred_skills), LOWER(?), ''))) / LENGTH(?) as skills_match_score
                FROM 
                    JobPostings jp
                LEFT JOIN 
                    Applications a ON jp.job_id = a.job_posting_id AND a.applicant_id = ?
                ORDER BY 
                    (IFNULL(description_match_score, 0) * 0.4 + IFNULL(skills_match_score, 0) * 0.4 + not_applied * 0.2) DESC
                LIMIT 10
            '''
            params = (user_skills_str, user_skills_str, user_skills_str, user_skills_str, user_id)
        else:
            query = '''
                SELECT 
                    jp.job_id,
                    jp.business_title,
                    jp.agency,
                    jp.work_location,
                    jp.salary_range_from,
                    jp.salary_range_to,
                    CASE 
                        WHEN a.job_posting_id IS NULL THEN 1
                        ELSE 0
                    END as not_applied
                FROM 
                    JobPostings jp
                LEFT JOIN 
                    Applications a ON jp.job_id = a.job_posting_id AND a.applicant_id = ?
                ORDER BY 
                    RANDOM()
                LIMIT 10
            '''
            params = (user_id,)

        logging.debug("Executing job recommendations query")
        cursor.execute(query, params)
        recommendations = cursor.fetchall()
        logging.debug(f"Found {len(recommendations)} recommendations")

        # Convert the results to a list of dictionaries
        recommendations_list = []
        for row in recommendations:
            job_dict = dict(row)
            if user_skills:
                job_dict['match_score'] = (job_dict.get('description_match_score', 0) * 0.4 + 
                                           job_dict.get('skills_match_score', 0) * 0.4 + 
                                           job_dict['not_applied'] * 0.2)
            else:
                job_dict['match_score'] = 0  # or some default value
            recommendations_list.append(job_dict)

        return jsonify(recommendations_list), 200

    except Exception as e:
        logging.error(f"Unexpected error in get_job_recommendations: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
@app.route('/applied_jobs', methods=['GET'])
def get_applied_jobs():
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT a.application_id, a.application_date, a.status,
                   j.job_id, j.business_title, j.agency, j.work_location,
                   j.job_description, j.salary_range_from, j.salary_range_to,
                   j.preferred_skills, j.additional_information
            FROM Applications a
            JOIN JobPostings j ON a.job_posting_id = j.job_id
            WHERE a.applicant_id = ?
        ''', (user_id,))
        applied_jobs = cursor.fetchall()
        
        applied_jobs_list = [
            {
                "application_id": job[0],
                "application_date": job[1],
                "status": job[2],
                "job_id": job[3],
                "business_title": job[4],
                "agency": job[5],
                "work_location": job[6],
                "job_description": job[7],
                "salary_range_from": job[8],
                "salary_range_to": job[9],
                "preferred_skills": job[10],
                "additional_information": job[11]
            } for job in applied_jobs
        ]
        
        return jsonify(applied_jobs_list), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/delete_application/<int:application_id>', methods=['DELETE'])
def delete_application(application_id):
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Check if the application exists and belongs to the user
        cursor.execute('''
            SELECT * FROM Applications 
            WHERE application_id = ? AND applicant_id = ?
        ''', (application_id, user_id))
        application = cursor.fetchone()
        
        if not application:
            return jsonify({"error": "Application not found or does not belong to the user"}), 404

        # Delete the application
        cursor.execute('DELETE FROM Applications WHERE application_id = ?', (application_id,))
        conn.commit()
        
        return jsonify({"message": "Application deleted successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/apply', methods=['POST'])
def apply_to_job():
    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    data = request.get_json()
    job_id = data.get('job_id')

    if not job_id:
        return jsonify({"error": "Job ID not provided"}), 400

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
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Session: {session}")
    print(f"Check auth: {current_user.is_authenticated}")  # Debug print
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user_id': current_user.id, 'name': current_user.name}), 200
    else:
        return jsonify({'authenticated': False}), 401
    
@app.route('/applicant_profile', methods=['GET', 'POST', 'OPTIONS'])
def applicant_profile():
    if request.method == 'OPTIONS':
        response = app.make_default_options_response()
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, User-Id'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
        return response

    user_id = request.headers.get('User-Id')
    if not user_id:
        return jsonify({"error": "User ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        # First, get the user's name from the Users table
        cursor.execute('SELECT name FROM Users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({"error": "User not found"}), 404
        
        user_name = user['name']

        # Then, get the applicant profile
        cursor.execute('SELECT * FROM Applicants WHERE user_id = ?', (user_id,))
        profile = cursor.fetchone()
        conn.close()

        if profile:
            profile_dict = dict(profile)
            profile_dict['name'] = user_name  # Add the user's name to the profile data
            return jsonify(profile_dict)
        else:
            return jsonify({"message": "Profile not found", "name": user_name}), 404

    elif request.method == 'POST':
        data = request.json
        cursor.execute('''
            INSERT OR REPLACE INTO Applicants 
            (user_id, resume_link, cover_letter, is_student, university, availability, employment_type, phone) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('resume_link'),
            data.get('cover_letter'),
            data.get('is_student'),
            data.get('university'),
            data.get('availability'),
            data.get('employment_type'),
            data.get('phone')
        ))
        conn.commit()

        # Fetch the user's name after updating the profile
        cursor.execute('SELECT name FROM Users WHERE user_id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()

        if user:
            return jsonify({"message": "Profile updated successfully", "name": user['name']}), 200
        else:
            return jsonify({"error": "User not found after profile update"}), 404

@app.route('/jobs', methods=['GET'])

def get_jobs():
    print(f"Current user authenticated: {current_user.is_authenticated}")
    print(f"Session: {session}")
    print(f"Current user ID: {current_user.get_id()}")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM JobPostings')
    jobs = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify([dict(row) for row in jobs])
     

@login_manager.unauthorized_handler
def unauthorized():
    if request.accept_mimetypes.accept_json:
        return jsonify({"error": "Unauthorized"}), 401
    return redirect(url_for('login'))



###############################EMPLOYER##########################################################
@app.route('/employer/job_postings', methods=['GET'])
def get_employer_job_postings():
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM JobPostings WHERE employer_id = ?', (employer_id,))
        job_postings = cursor.fetchall()
        job_count = len(job_postings)
        return jsonify({
            "job_count": job_count,
            "job_postings": [dict(ix) for ix in job_postings]
        }), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/employer/create_job', methods=['POST'])
def create_job_posting():
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO JobPostings (
                job_id, employer_id, business_title, agency, work_location,
                job_description, salary_range_from, salary_range_to,
                preferred_skills, additional_information, posting_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['job_id'], employer_id, data['business_title'], data['agency'],
            data['work_location'], data['job_description'],
            data['salary_range_from'], data['salary_range_to'],
            data['preferred_skills'], data['additional_information'],
            datetime.now().strftime('%Y-%m-%d')
        ))
        conn.commit()
        
        return jsonify({"message": "Job posting created successfully", "job_id": data['job_id']}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Job ID already exists"}), 400
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
@app.route('/employer/update_job/<int:job_id>', methods=['PUT'])
def update_job_posting(job_id):
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    data = request.json
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE JobPostings SET
                business_title = ?, agency = ?, work_location = ?,
                job_description = ?, salary_range_from = ?, salary_range_to = ?,
                preferred_skills = ?, additional_information = ?
            WHERE job_id = ? AND employer_id = ?
        ''', (
            data['business_title'], data['agency'], data['work_location'],
            data['job_description'], data['salary_range_from'], data['salary_range_to'],
            data['preferred_skills'], data['additional_information'],
            job_id, employer_id
        ))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Job posting not found or does not belong to this employer"}), 404
        return jsonify({"message": "Job posting updated successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/employer/job_applications/<int:job_id>', methods=['GET'])
def get_job_applications(job_id):
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT a.*, u.name as applicant_name, u.email as applicant_email, 
                   ap.resume_link, ap.cover_letter, ap.is_student, ap.university, 
                   ap.availability, ap.employment_type, ap.phone
            FROM Applications a
            JOIN Users u ON a.applicant_id = u.user_id
            JOIN Applicants ap ON a.applicant_id = ap.user_id
            JOIN JobPostings j ON a.job_posting_id = j.job_id
            WHERE j.job_id = ? AND j.employer_id = ?
        ''', (job_id, employer_id))
        applications = cursor.fetchall()
        
        application_count = len(applications)
        
        return jsonify({
            "applications": [dict(ix) for ix in applications],
            "count": application_count
        }), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


### CHeck count applications 
@app.route('/employer/count_applications/<int:job_id>', methods=['GET'])
def count_job_applications(job_id):
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
        SELECT COUNT(*) AS total_applications
        FROM Applications a
        JOIN Users u ON a.applicant_id = u.user_id
        JOIN JobPostings j ON a.job_posting_id = j.job_id
        WHERE j.job_id = ? AND j.employer_id = ?
        ''', (job_id, employer_id))
        applications = cursor.fetchall()
        return jsonify([dict(ix) for ix in applications]), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/employer/update_application_status/<int:application_id>', methods=['PUT'])
def update_application_status(application_id):
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    data = request.json
    new_status = data.get('status')
    if not new_status:
        return jsonify({"error": "New status not provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            UPDATE Applications SET status = ?
            WHERE application_id = ? AND
                  job_posting_id IN (SELECT job_id FROM JobPostings WHERE employer_id = ?)
        ''', (new_status, application_id, employer_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Application not found or does not belong to a job posting by this employer"}), 404
        return jsonify({"message": "Application status updated successfully"}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/employer/delete_job/<int:job_id>', methods=['DELETE'])
def delete_job_posting(job_id):
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # First, check if the job posting belongs to the employer
        cursor.execute('SELECT * FROM JobPostings WHERE job_id = ? AND employer_id = ?', (job_id, employer_id))
        job = cursor.fetchone()
        
        if not job:
            return jsonify({"error": "Job posting not found or you don't have permission to delete it"}), 404
        
        # If the job exists and belongs to the employer, delete it
        cursor.execute('DELETE FROM JobPostings WHERE job_id = ?', (job_id,))
        conn.commit()
        
        return jsonify({"message": "Job posting deleted successfully"}), 200
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()




@app.route('/employer/total_applications', methods=['GET'])
def get_total_applications():
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT COUNT(*) as total_applications
            FROM Applications a
            JOIN JobPostings j ON a.job_posting_id = j.job_id
            WHERE j.employer_id = ?
        ''', (employer_id,))
        result = cursor.fetchone()
        return jsonify({"total_applications": result['total_applications']}), 200
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/employer/top_performing_job', methods=['GET'])
def get_top_performing_job():
    employer_id = request.headers.get('User-Id')
    if not employer_id:
        return jsonify({"error": "Employer ID not provided"}), 401

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT j.job_id, j.business_title, COUNT(*) as application_count
            FROM JobPostings j
            LEFT JOIN Applications a ON j.job_id = a.job_posting_id
            WHERE j.employer_id = ?
            GROUP BY j.job_id
            ORDER BY application_count DESC
            LIMIT 1
        ''', (employer_id,))
        result = cursor.fetchone()
        if result:
            return jsonify({
                "job_id": result['job_id'],
                "business_title": result['business_title'],
                "application_count": result['application_count']
            }), 200
        else:
            return jsonify({"message": "No job postings found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    finally:
        cursor.close()
        conn.close()
if __name__ == '__main__':
    app.run(debug=True)
