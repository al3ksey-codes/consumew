import os
import psycopg2
import psycopg2.extras

# Storage limit in bytes (10 MB)
STORAGE_LIMIT = 10 * 1024 * 1024


def get_db_connection():
    """
    Returns a new PostgreSQL database connection using credentials from environment variables.
    Make sure the following environment variables are set:
      - DB_HOST: hostname of your PostgreSQL server (should not be 'localhost' on Vercel)
      - DB_NAME: database name
      - DB_USER: database user
      - DB_PASSWORD: database user's password
      - DB_PORT: database port (optional, defaults to 5432)
    """
    DB_HOST = os.getenv("POSTGRES_HOST")
    DB_NAME = os.getenv("PGDATABASE")
    DB_USER = os.getenv("PGUSER")
    DB_PASSWORD = os.getenv("PGPASSWORD")
    DB_PORT = 5432

    # Check if required variables are provided.
    if not DB_HOST or not DB_NAME or not DB_USER or not DB_PASSWORD:
        raise Exception("Missing one or more PostgreSQL connection environment variables: "
                        "DB_HOST, DB_NAME, DB_USER, DB_PASSWORD.")

    # Connect to PostgreSQL using psycopg2.
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn


def init_db():
    """
    Creates the 'messages' table in the PostgreSQL database if it doesn't exist.
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
    Uses a DictCursor for dictionary-like row access.
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
