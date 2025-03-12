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

# Initialize DB and scheduler
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

@app.template_filter('format_timestamp')
def format_timestamp(ts):
    try:
        dt = datetime.datetime.fromisoformat(ts)
        formatted = dt.strftime("%Y-%m-%d T %H:%M:%S.%f")[:-3]
        formatted += ", UTC+1"
        return formatted
    except Exception:
        return ts

@app.route('/')
def index():
    messages = models.get_messages()
    # Reverse messages so newest are on top
    messages = list(reversed(messages))
    node_name = config.CONFIG.get("NODE_NAME", "Node1")
    fancy_sender = config.CONFIG.get("FANCY_SENDER_FORMAT", False)
    node_addresses = config.CONFIG.get("NODE_ADDRESSES", [])
    return render_template('index.html', messages=messages, node_name=node_name, 
                           fancy_sender=fancy_sender, node_addresses=node_addresses)

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

@app.route('/messages_json')
def messages_json():
    messages = models.get_messages()
    messages = list(reversed(messages))
    messages_list = [dict(msg) for msg in messages]
    return jsonify(messages_list)

# New route to clear messages table
@app.route('/clear_messages', methods=['POST'])
@basic_auth.required
def clear_messages():
    models.clear_messages()
    flash('Messages cleared successfully', 'success')
    return redirect(url_for('admin'))

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
            "NODE_ADDRESSES": request.form.get('node_addresses', ""),
            "FANCY_SENDER_FORMAT": True if request.form.get('fancy_sender_format') == "on" else False
        }
        addresses = [addr.strip() for addr in new_config["NODE_ADDRESSES"].split(',') if addr.strip()]
        new_config["NODE_ADDRESSES"] = addresses
        config.update_config(new_config)
        flash('Configuration updated', 'success')
        return redirect(url_for('admin'))
    # Get current messages count
    messages_count = len(models.get_messages())
    return render_template('admin.html', config=config.CONFIG, messages_count=messages_count)

@app.route('/admin_home')
@basic_auth.required
def admin_home():
    # Redirect to the main page.
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
