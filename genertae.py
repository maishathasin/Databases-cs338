import sqlite3

def execute_queries(db_path, sql_file, output_file):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    with open(sql_file, 'r') as file:
        queries = file.read().split(';')
    
    results = []
    for query in queries:
        if query.strip():
            cursor.execute(query)
            if query.strip().lower().startswith('select'):
                results.append(cursor.fetchall())
            else:
                conn.commit()
                results.append(cursor.execute('SELECT * FROM Applications').fetchall())
    
    with open(output_file, 'w') as file:
        for result in results:
            for row in result:
                file.write('|'.join(map(str, row)) + '\n')
            file.write('\n')
    
    cursor.close()
    conn.close()

if __name__ == '__main__':
    db_path = 'job_portal.db'
    sql_file = 'test-sample.sql'
    output_file = 'test-sample.out'
    
    execute_queries(db_path, sql_file, output_file)
