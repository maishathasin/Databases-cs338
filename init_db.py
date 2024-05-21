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
        profile_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Jobs (
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        company TEXT NOT NULL,
        description TEXT,
        posting_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        application_deadline TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_id INTEGER NOT NULL,
        application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'applied',
        FOREIGN KEY (user_id) REFERENCES Users(user_id),
        FOREIGN KEY (job_id) REFERENCES Jobs(job_id)
    )
    ''')

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    initialise()
