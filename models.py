import os
import psycopg2
import psycopg2.extras

# Storage limit in bytes (10 MB)
STORAGE_LIMIT = 10 * 1024 * 1024

def get_db_connection():
    """
    Returns a new PostgreSQL database connection using credentials from environment variables.
    """
    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "your_db_name"),
        user=os.getenv("DB_USER", "your_db_user"),
        password=os.getenv("DB_PASSWORD", "your_db_password"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", 5432)
    )
    return conn

def init_db():
    """
    Creates the 'messages' table if it doesn't exist.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id SERIAL PRIMARY KEY,
            sender TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            message TEXT NOT NULL
        );
    ''')
    conn.commit()
    cur.close()
    conn.close()

def add_message(sender, timestamp, message):
    """
    Inserts a new message record into the 'messages' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (sender, timestamp, message) VALUES (%s, %s, %s)",
        (sender, timestamp, message)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_messages():
    """
    Retrieves all messages in ascending order by id.
    Uses a DictCursor to allow dictionary-like access to rows.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM messages ORDER BY id ASC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def purge_old_messages():
    """
    Purges the oldest messages until the total table size is below STORAGE_LIMIT.
    Uses PostgreSQL's pg_total_relation_size to check the size of the 'messages' table.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT pg_total_relation_size('messages')")
    size = cur.fetchone()[0]
    while size > STORAGE_LIMIT:
        cur.execute("""
            DELETE FROM messages 
            WHERE id = (SELECT id FROM messages ORDER BY id ASC LIMIT 1)
        """)
        conn.commit()
        cur.execute("SELECT pg_total_relation_size('messages')")
        size = cur.fetchone()[0]
    cur.close()
    conn.close()
