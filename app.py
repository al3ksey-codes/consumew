from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import threading
import time
import schedule
import datetime
import os
from flask_basicauth import BasicAuth

import config
import models
import tasks

app = Flask(__name__)
app.config.from_object('config.Config')

basic_auth = BasicAuth(app)

# Initialize DB and scheduler (unchanged)
models.init_db()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(app.config['DISPATCH_INTERVAL']).minutes.do(tasks.dispatch_messages)
schedule.every(app.config['PING_INTERVAL']).minutes.do(tasks.ping_nodes)
schedule.every(5).minutes.do(models.purge_old_messages)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Jinja filter for formatting timestamps
@app.template_filter('format_timestamp')
def format_timestamp(ts):
    try:
        dt = datetime.datetime.fromisoformat(ts)
        # Format: "YYYY-MM-DD T HH:MM:SS.mmm, UTC+1"
        formatted = dt.strftime("%Y-%m-%d T %H:%M:%S.%f")[:-3]  # trim microseconds to milliseconds
        formatted += ", UTC+1"
        return formatted
    except Exception:
        return ts

@app.route('/')
def index():
    messages = models.get_messages()
    # Reverse messages so that the newest are on top
    messages = list(reversed(messages))
    node_name = config.CONFIG.get("NODE_NAME", "Node1")
    return render_template('index.html', messages=messages, node_name=node_name)

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    required_fields = ['sender', 'timestamp', 'message']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400
    models.add_message(data['sender'], data['timestamp'], data['message'])
    return jsonify({'status': 'Message received'}), 200

# New JSON endpoint for AJAX polling
@app.route('/messages_json')
def messages_json():
    messages = models.get_messages()
    messages = list(reversed(messages))
    # Convert each row to a dict (if not already)
    messages_list = [dict(msg) for msg in messages]
    return jsonify(messages_list)

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    if request.method == 'POST':
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
        addresses = [addr.strip() for addr in new_config["NODE_ADDRESSES"].split(',') if addr.strip()]
        new_config["NODE_ADDRESSES"] = addresses
        config.update_config(new_config)
        flash('Configuration updated', 'success')
        return redirect(url_for('admin'))
    return render_template('admin.html', config=config.CONFIG)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import threading
import time
import schedule
import datetime
import os
from flask_basicauth import BasicAuth

import config
import models
import tasks

app = Flask(__name__)
app.config.from_object('config.Config')

basic_auth = BasicAuth(app)

# Initialize DB and scheduler (unchanged)
models.init_db()

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

schedule.every(app.config['DISPATCH_INTERVAL']).minutes.do(tasks.dispatch_messages)
schedule.every(app.config['PING_INTERVAL']).minutes.do(tasks.ping_nodes)
schedule.every(5).minutes.do(models.purge_old_messages)
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()

# Jinja filter for formatting timestamps
@app.template_filter('format_timestamp')
def format_timestamp(ts):
    try:
        dt = datetime.datetime.fromisoformat(ts)
        # Format: "YYYY-MM-DD T HH:MM:SS.mmm, UTC+1"
        formatted = dt.strftime("%Y-%m-%d T %H:%M:%S.%f")[:-3]  # trim microseconds to milliseconds
        formatted += ", UTC+1"
        return formatted
    except Exception:
        return ts

@app.route('/')
def index():
    messages = models.get_messages()
    # Reverse messages so that the newest are on top
    messages = list(reversed(messages))
    node_name = config.CONFIG.get("NODE_NAME", "Node1")
    return render_template('index.html', messages=messages, node_name=node_name)

@app.route('/receive', methods=['POST'])
def receive():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Invalid JSON'}), 400
    required_fields = ['sender', 'timestamp', 'message']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing fields'}), 400
    models.add_message(data['sender'], data['timestamp'], data['message'])
    return jsonify({'status': 'Message received'}), 200

# New JSON endpoint for AJAX polling
@app.route('/messages_json')
def messages_json():
    messages = models.get_messages()
    messages = list(reversed(messages))
    # Convert each row to a dict (if not already)
    messages_list = [dict(msg) for msg in messages]
    return jsonify(messages_list)

@app.route('/admin', methods=['GET', 'POST'])
@basic_auth.required
def admin():
    if request.method == 'POST':
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
        addresses = [addr.strip() for addr in new_config["NODE_ADDRESSES"].split(',') if addr.strip()]
        new_config["NODE_ADDRESSES"] = addresses
        config.update_config(new_config)
        flash('Configuration updated', 'success')
        return redirect(url_for('admin'))
    return render_template('admin.html', config=config.CONFIG)

if __name__ == '__main__':
    app.run(debug=True)
