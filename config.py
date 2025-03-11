import json
import os

CONFIG_FILE = 'config.json'

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
    global CONFIG
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            CONFIG = json.load(f)

def save_config():
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG, f, indent=4)

def update_config(new_config):
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
