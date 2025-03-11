import sqlite3
import os

DB_FILE = 'data.db'
STORAGE_LIMIT = 10 * 1024 * 1024  # 10 MB

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_message(sender, timestamp, message):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (sender, timestamp, message) VALUES (?, ?, ?)',
                (sender, timestamp, message))
    conn.commit()
    conn.close()

def get_messages():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM messages ORDER BY id ASC')
    rows = cur.fetchall()
    conn.close()
    return rows

def purge_old_messages():
    # If the database file exceeds STORAGE_LIMIT, delete the oldest messages.
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > STORAGE_LIMIT:
        conn = get_db_connection()
        cur = conn.cursor()
        while os.path.getsize(DB_FILE) > STORAGE_LIMIT:
            cur.execute('DELETE FROM messages WHERE id = (SELECT id FROM messages ORDER BY id ASC LIMIT 1)')
            conn.commit()
        conn.close()
