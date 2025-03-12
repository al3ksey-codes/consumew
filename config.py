import json
import psycopg2
import psycopg2.extras
from models import get_db_connection  # use your existing DB connection function

# Default configuration values.
DEFAULT_CONFIG = {
    "BASIC_AUTH_USERNAME": "admin",
    "BASIC_AUTH_PASSWORD": "password",
    "OPENAI_API_KEY": "",
    "OPENAI_PROMPT": "Generate some data based on input:",
    "DATA_GENERATION_METHOD": "random",  # "openai" or "random"
    "RANDOM_STRING_LENGTH": 16,
    "RANDOM_STRING_CASE": "camel",  # options: "uppercase", "lowercase", "camel"
    "DISPATCH_INTERVAL": 1,  # in minutes
    "DISPATCH_AMOUNT": 1,
    "PING_INTERVAL": 5,      # in minutes
    "NODE_NAME": "Randio_",
    "NODE_ADDRESSES": []     # list of other node addresses (e.g., "192.168.1.2:5000")
}

TABLE_NAME = "configuration"

def init_config_db():
    """
    Creates the configuration table if it doesn't exist and inserts a default row with id=1.
    The entire configuration is stored as JSON in a single row.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    # Create table with a fixed primary key type (INTEGER) instead of SERIAL.
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY,
            config_data JSONB NOT NULL
        );
    """)
    # Insert a default configuration row with id=1 if it doesn't exist.
    cur.execute(f"""
        INSERT INTO {TABLE_NAME} (id, config_data)
        VALUES (1, %s)
        ON CONFLICT (id) DO NOTHING;
    """, (json.dumps(DEFAULT_CONFIG),))
    conn.commit()
    cur.close()
    conn.close()

# Initialize the configuration table on module load.
init_config_db()

def load_config():
    """
    Loads the configuration from the database.
    Returns a dictionary with the configuration.
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute(f"SELECT config_data FROM {TABLE_NAME} WHERE id = 1")
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        # If config_data is stored as JSONB, psycopg2 returns a dict directly.
        return row['config_data'] if isinstance(row['config_data'], dict) else json.loads(row['config_data'])
    return DEFAULT_CONFIG.copy()

def save_config(new_config):
    """
    Saves the given configuration dictionary to the database.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(f"UPDATE {TABLE_NAME} SET config_data = %s WHERE id = 1", (json.dumps(new_config),))
    conn.commit()
    cur.close()
    conn.close()

# Load configuration into a global variable.
CONFIG = load_config()

def update_config(new_config):
    """
    Update the in-memory configuration with new values and persist it to the database.
    """
    global CONFIG
    CONFIG.update(new_config)
    save_config(CONFIG)

class Config:
    DEBUG = True
    SECRET_KEY = 'supersecretkey'
    BASIC_AUTH_USERNAME = CONFIG.get("BASIC_AUTH_USERNAME", "admin")
    BASIC_AUTH_PASSWORD = CONFIG.get("BASIC_AUTH_PASSWORD", "password")
    DISPATCH_INTERVAL = CONFIG.get("DISPATCH_INTERVAL", 5)
    PING_INTERVAL = CONFIG.get("PING_INTERVAL", 5)
