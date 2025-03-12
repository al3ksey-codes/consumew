import json
import os

# When running on Vercel, the root directory is read-only.
# We check if the VERCEL environment variable is present (Vercel sets VERCEL=true)
# and use /tmp for writes. Otherwise, we use config.json in the current directory.
if os.environ.get("VERCEL"):
    CONFIG_FILE = "/tmp/config.json"
else:
    CONFIG_FILE = "config.json"

# Default configuration values.
CONFIG = {
    "BASIC_AUTH_USERNAME": "admin",
    "BASIC_AUTH_PASSWORD": "password",
    "OPENAI_API_KEY": "",
    "OPENAI_PROMPT": "Generate some data based on input:",
    "DATA_GENERATION_METHOD": "random",  # "openai" or "random"
    "RANDOM_STRING_LENGTH": 16,
    "RANDOM_STRING_CASE": "camel",  # options: "uppercase", "lowercase", "camel"
    "DISPATCH_INTERVAL": 5,  # in minutes
    "DISPATCH_AMOUNT": 1,
    "PING_INTERVAL": 5,      # in minutes
    "NODE_NAME": "Node1",
    "NODE_ADDRESSES": []     # list of other node addresses (e.g., "192.168.1.2:5000")
}

def load_config():
    """
    Load the configuration from CONFIG_FILE if it exists.
    On Vercel, this file will be in /tmp and is ephemeral.
    """
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                CONFIG = json.load(f)
        except Exception as e:
            print(f"Failed to load config from {CONFIG_FILE}: {e}")

def save_config():
    """
    Save the current configuration to CONFIG_FILE.
    On Vercel, writes to /tmp are allowed.
    """
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG, f, indent=4)
    except Exception as e:
        print(f"Failed to save config to {CONFIG_FILE}: {e}")

def update_config(new_config):
    """
    Update the in-memory configuration with new values and write them to disk.
    """
    global CONFIG
    CONFIG.update(new_config)
    save_config()

# Load configuration on startup.
load_config()

class Config:
    DEBUG = True
    SECRET_KEY = 'supersecretkey'
    # Settings for Flask-BasicAuth
    BASIC_AUTH_USERNAME = CONFIG.get("BASIC_AUTH_USERNAME", "admin")
    BASIC_AUTH_PASSWORD = CONFIG.get("BASIC_AUTH_PASSWORD", "password")
    # Scheduler intervals
    DISPATCH_INTERVAL = CONFIG.get("DISPATCH_INTERVAL", 5)
    PING_INTERVAL = CONFIG.get("PING_INTERVAL", 5)
