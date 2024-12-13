import sqlite3

def create_db():
    conn = sqlite3.connect('parking_details.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS parking_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        free_spaces INTEGER NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

create_db()
