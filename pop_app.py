import csv
import sqlite3
from datetime import datetime

def import_applicants_csv_to_db(csv_file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        
        for row in reader:
            cursor.execute('''
                INSERT INTO Applicants (
                    user_id, resume_link, cover_letter, is_student, university, availability, 
                    employment_type, phone
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row['ID'], row['Resume'], row['Cover Letter'], 
                1 if row['Student'].lower() == 'yes' else 0, row['University'], 
                row['Availability'], row['Employment Type'], row['Phone']
            ))
    
    conn.commit()
    cursor.close()
    conn.close()


# generates synthetic applications from applicants and puts them in the first two JobPOstings
def generate_synthetic_applications(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT applicant_id FROM Applicants LIMIT 2")
    applicant_ids = [row[0] for row in cursor.fetchall()]
    
    cursor.execute("SELECT job_posting_id FROM JobPostings LIMIT 2")
    job_posting_ids = [row[0] for row in cursor.fetchall()]
    
    application_data = []
    status_options = ['Applied', 'Reviewed', 'Interviewed', 'Hired']
    for applicant_id in applicant_ids:
        for job_posting_id in job_posting_ids:
            application_date = datetime.now().date()
            status = status_options[applicant_id % len(status_options)]  # Simple synthetic status assignment
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
    
    # Import applicants from CSV
    import_applicants_csv_to_db(applicants_csv_file_path, db_path)
    
    # Generate synthetic applications
    generate_synthetic_applications(db_path)
