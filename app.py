from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import threading
import time
import schedule
import datetime
import os

from flask_basicauth import BasicAuth

# Import our own modules
import config
import models
import tasks

app = Flask(__name__)
app.config.from_object('config.Config')  # load settings from config.py

# Initialize Basic Authentication for protected routes.
basic_auth = BasicAuth(app)

# Initialize the SQLite database (creates tables if not present)
models.init_db()

# Background scheduler runner
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Schedule periodic tasks using intervals from the config.
schedule.every(app.config['DISPATCH_INTERVAL']).minutes.do(tasks.dispatch_messages)
schedule.every(app.config['PING_INTERVAL']).minutes.do(tasks.ping_nodes)
schedule.every(5).minutes.do(models.purge_old_messages)  # periodically check storage

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Main page – displays all messages in a messenger-like view.
@app.route('/')
def index():
    messages = models.get_messages()
    return render_template('index.html', messages=messages)

# Endpoint to receive incoming messages from other nodes.
@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    # Validate required fields
    required_fields = ['sender', 'timestamp', 'message']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400
    # Save message in the database.
    models.add_message(data['sender'], data['timestamp'], data['message'])
    return jsonify({'status': 'Message received'}), 200

# Backend configuration interface (protected via basic auth)
@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    if request.method == 'POST':
        # Update configuration from form fields.
        new_config = {
            "OPENAI_API_KEY": request.form.get('openai_api_key', config.CONFIG.get("OPENAI_API_KEY", "")),
            "OPENAI_PROMPT": request.form.get('openai_prompt', config.CONFIG.get("OPENAI_PROMPT", "")),
            "DATA_GENERATION_METHOD": request.form.get('data_generation_method', config.CONFIG.get("DATA_GENERATION_METHOD", "random")),
            "RANDOM_STRING_LENGTH": int(request.form.get('random_string_length', config.CONFIG.get("RANDOM_STRING_LENGTH", 16))),
            "RANDOM_STRING_CASE": request.form.get('random_string_case', config.CONFIG.get("RANDOM_STRING_CASE", "camel")),
            "DISPATCH_INTERVAL": int(request.form.get('dispatch_interval', app.config['DISPATCH_INTERVAL'])),
            "DISPATCH_AMOUNT": int(request.form.get('dispatch_amount', config.CONFIG.get("DISPATCH_AMOUNT", 1))),
            "PING_INTERVAL": int(request.form.get('ping_interval', app.config['PING_INTERVAL'])),
            "NODE_NAME": request.form.get('node_name', config.CONFIG.get("NODE_NAME", "Node1")),
            "NODE_ADDRESSES": request.form.get('node_addresses', "")
        }
        # Process comma-separated node addresses into a list.
        addresses = [addr.strip() for addr in new_config["NODE_ADDRESSES"].split(',') if addr.strip()]
        new_config["NODE_ADDRESSES"] = addresses

        config.update_config(new_config)
        flash('Configuration updated', 'success')
        return redirect(url_for('admin'))
    return render_template('admin.html', config=config.CONFIG)

if __name__ == '__main__':
    app.run(debug=True)
