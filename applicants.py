import csv
import random

def generate_applicant_data(num_applicants):
    universities = ['University of ABC', 'XYZ College', 'PQR Institute', 'LMN University', 'EFG Tech']
    availability_options = ['Summer', 'Winter', 'Fall']
    employment_types = ['Full Time', 'Part Time', 'Coop/Internship']

    data = []
    for i in range(num_applicants):
        applicant = {
            'ID': i + 1,
            'Name': f'Applicant {i + 1}',
            'Resume': f'https://drive.google.com/resume_{i + 1}',
            'Cover Letter': f'Cover Letter {i + 1}',
            'Student': random.choice(['Yes', 'No']),
            'University': random.choice(universities),
            'Availability': random.choice(availability_options),
            'Employment Type': random.choice(employment_types),
            'Email': f'applicant{i + 1}@example.com',
            'Phone': f'+1-{random.randint(100, 999)}-{random.randint(100, 999)}-{random.randint(1000, 9999)}'
        }
        data.append(applicant)

    return data

def save_to_csv(data, filename):
    fieldnames = ['ID', 'Name', 'Resume', 'Cover Letter', 'Student', 'University',
                  'Availability', 'Employment Type', 'Email', 'Phone']

    with open(filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

applicant_data = generate_applicant_data(50)

save_to_csv(applicant_data, 'applicants.csv')


