import sqlite3
import csv


## this script takes the data from the tables and puts them into a sample csv
def fetch_and_save_rows_to_csv(db_path, table_name, csv_file_path, limit=10):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
    rows = cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]

    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(column_names)  
        writer.writerows(rows)         

    cursor.close()
    conn.close()

if __name__ == '__main__':
    db_path = 'job_portal.db'
    table_name = 'Users'
    csv_file_path = 'Users_sample.csv'
    fetch_and_save_rows_to_csv(db_path, table_name, csv_file_path)
