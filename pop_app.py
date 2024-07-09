import csv
import sqlite3
from datetime import datetime

def import_csv(csv_file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            cursor.execute('''
                INSERT INTO Users (name, email, password, user_type)
                VALUES (?, ?, ?, ?)
            ''', (
                row['Name'], row['Email'], 'password', 'applicant'
            ))

            user_id = cursor.lastrowid

            
            cursor.execute('''
                INSERT INTO Applicants (
                    user_id, resume_link, cover_letter, is_student, university, availability, 
                    employment_type, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, row['Resume'], row['Cover Letter'], 
                1 if row['Student'].lower() == 'yes' else 0, row['University'], 
                row['Availability'], row['Employment Type'], row['Phone']
            ))
    
    conn.commit()
    cursor.close()
    conn.close()

def generate(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT applicant_id FROM Applicants LIMIT 500")
    applicant_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT job_posting_id FROM JobPostings LIMIT 500")
    job_posting_ids = [row[0] for row in cursor.fetchall()]
    
    application_data = []
    #synthetically add the applicants
    options = ['Applied', 'Reviewed', 'Interviewed', 'Hired']
    for applicant_id in applicant_ids:
        for job_posting_id in job_posting_ids:
            application_date = datetime.now().date()
            status = options[applicant_id % len(options)]  
            application_data.append((job_posting_id, applicant_id, application_date, status))
    
    cursor.executemany('''
        INSERT INTO Applications (
            job_posting_id, applicant_id, application_date, status
        ) VALUES (?, ?, ?, ?)
    ''', application_data)
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    db_path = 'job_portal.db'
    applicants_csv_file_path = 'applicants.csv'
    
    import_csv(applicants_csv_file_path, db_path)
    
    generate(db_path)
