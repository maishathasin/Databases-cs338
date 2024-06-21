import sqlite3

def initialise():
    conn = sqlite3.connect('job_portal.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        user_type TEXT CHECK(user_type IN ('employer', 'applicant')) NOT NULL,
        profile_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
   CREATE TABLE Applicants (
    applicant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    resume_link TEXT,
    cover_letter TEXT,
    is_student BOOLEAN,
    university TEXT,
    availability TEXT,
    employment_type TEXT,
    phone TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

    ''')

    cursor.execute('''
   CREATE TABLE Employers (
    employer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    company_name TEXT,
    recruitment_contact TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);
    ''')


    cursor.execute('''

CREATE TABLE IF NOT EXISTS JobPostings (
    job_posting_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employer_id INTEGER,
    job_id INTEGER,
    agency TEXT,
    posting_type TEXT,
    num_positions INTEGER,
    business_title TEXT,
    civil_service_title TEXT,
    title_code_no TEXT,
    level TEXT,
    job_category TEXT,
    full_time_part_time TEXT,
    salary_range_from REAL,
    salary_range_to REAL,
    salary_frequency TEXT,
    work_location TEXT,
    division_work_unit TEXT,
    job_description TEXT,
    min_qual_requirements TEXT,
    preferred_skills TEXT,
    additional_information TEXT,
    to_apply TEXT,
    hours_shift TEXT,
    work_location_1 TEXT,
    recruitment_contact TEXT,
    residency_requirement TEXT,
    posting_date DATE,
    post_until DATE,
    posting_updated DATE,
    process_date DATE,
    FOREIGN KEY (employer_id) REFERENCES Employers(employer_id)
);
    ''')

    cursor.execute('''
    CREATE TABLE Applications (
    application_id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_posting_id INTEGER,
    applicant_id INTEGER,
    application_date DATE,
    status TEXT,
    FOREIGN KEY (job_posting_id) REFERENCES JobPostings(job_posting_id),
    FOREIGN KEY (applicant_id) REFERENCES Applicants(applicant_id)
);
    ''')

    # Create trigger to prevent duplicate applications
    cursor.execute('''
    CREATE TRIGGER IF NOT EXISTS prevent_duplicate_applications
    BEFORE INSERT ON Applications
    FOR EACH ROW
    BEGIN
        SELECT CASE
            WHEN ((SELECT COUNT(*) FROM Applications WHERE job_posting_id = NEW.job_posting_id AND applicant_id = NEW.applicant_id) > 0)
            THEN RAISE (ABORT, 'Duplicate application detected')
        END;
    END;
    ''')

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    initialise()
