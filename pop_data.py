import csv
import sqlite3
from datetime import datetime

def import_csv(csv_file_path, db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        # take the first 100 only 
        reader = reader[100]
        
        for row in reader:
            try:
                posting_date = datetime.strptime(row['Posting Date'], '%Y-%m-%dT%H:%M:%S').date() if row['Posting Date'] else None
                post_until = datetime.strptime(row['Post Until'], '%Y-%m-%dT%H:%M:%S').date() if row['Post Until'] else None
                posting_updated = datetime.strptime(row['Posting Updated'], '%Y-%m-%dT%H:%M:%S').date() if row['Posting Updated'] else None
                process_date = datetime.strptime(row['Process Date'], '%Y-%m-%dT%H:%M:%S').date() if row['Process Date'] else None
                
                # employer_id based on the agency name
                # 
                cursor.execute('SELECT employer_id FROM Employers WHERE company_name = ?', (row['Agency'],))
                result = cursor.fetchone()
                if result:
                    employer_id = result[0]
                else:
                    print(f"Employer not found for agency: {row['Agency']}")
                    continue
                
                cursor.execute('''
                    INSERT INTO JobPostings (
                        employer_id, job_id, agency, posting_type, num_positions, business_title, 
                        civil_service_title, title_code_no, level, job_category, full_time_part_time, 
                        salary_range_from, salary_range_to, salary_frequency, work_location, 
                        division_work_unit, job_description, min_qual_requirements, preferred_skills, 
                        additional_information, to_apply, hours_shift, work_location_1, 
                        recruitment_contact, residency_requirement, posting_date, post_until, 
                        posting_updated, process_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    employer_id, row['Job ID'], row['Agency'], row['Posting Type'], row['# Of Positions'], 
                    row['Business Title'], row['Civil Service Title'], row['Title Code No'], row['Level'], 
                    row['Job Category'], row['Full-Time/Part-Time indicator'], row['Salary Range From'], 
                    row['Salary Range To'], row['Salary Frequency'], row['Work Location'], 
                    row['Division/Work Unit'], row['Job Description'], row['Minimum Qual Requirements'], 
                    row['Preferred Skills'], row['Additional Information'], row['To Apply'], 
                    row['Hours/Shift'], row['Work Location 1'], row['Recruitment Contact'], 
                    row['Residency Requirement'], posting_date, post_until, posting_updated, process_date
                ))
            except ValueError as e:
                print(f"ValueError: {e} for row: {row}")
            except KeyError as e:
                print(f"KeyError: {e} for row: {row}")
    
    conn.commit()
    cursor.close()
    conn.close()
if __name__ == '__main__':
    csv_file_path = 'nyc-jobs-1 1.csv'
    db_path = 'job_portal.db'
    import_csv(csv_file_path, db_path)
