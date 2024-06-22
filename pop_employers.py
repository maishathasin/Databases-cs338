import csv
import sqlite3


def import_csv(csv_file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        unique_employers = {}
        for row in reader:
            company_name = row['Agency']
            recruitment_contact = row['Recruitment Contact']

            if company_name not in unique_employers:
                unique_employers[company_name] = recruitment_contact

        for company_name, recruitment_contact in unique_employers.items():
            cursor.execute('''
                INSERT INTO Users (name, email, password, user_type)
                VALUES (?, ?, ?, ?)
            ''', (
                company_name, f'{company_name.replace(" ", "").lower()}@example.com', 'password', 'employer'
            ))

            user_id = cursor.lastrowid

            cursor.execute('''
                INSERT INTO Employers (
                    user_id, company_name, recruitment_contact
                ) VALUES (?, ?, ?)
            ''', (
                user_id, company_name, recruitment_contact
            ))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    db_path = 'job_portal.db'
    
    import_csv('nyc-jobs-1 1.csv', db_path)
