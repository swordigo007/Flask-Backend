from flask import Flask, request, jsonify
from datetime import datetime
import threading

app = Flask(__name__)

# Data stores
device_logs = []       # Logs sent by devices
commands = []          # Commands to send to devices
device_status = {}     # Latest status of each device

# Lock for thread safety
lock = threading.Lock()

@app.route('/update_log', methods=['POST'])
def update_log():
    data = request.get_json()
    if not data or 'log' not in data:
        return jsonify({'status': 'error', 'message': 'Missing log'}), 400
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'log': data['log']
    }
    with lock:
        device_logs.append(log_entry)
    return jsonify({'status': 'success', 'log': log_entry})

@app.route('/get_commands', methods=['GET'])
def get_commands():
    with lock:
        current_commands = list(commands)
        # Optional: clear commands after sending
        # commands.clear()
    return jsonify({'commands': current_commands})

@app.route('/update_status', methods=['POST'])
def update_status():
    data = request.get_json()
    if not data or 'device_id' not in data or 'status' not in data:
        return jsonify({'status': 'error', 'message': 'Missing device_id or status'}), 400
    device_id = data['device_id']
    status_info = data['status']
    timestamp = datetime.utcnow().isoformat()
    with lock:
        device_status[device_id] = {
            'status': status_info,
            'timestamp': timestamp
        }
    return jsonify({'status': 'success', 'device_id': device_id, 'timestamp': timestamp})

@app.route('/add_command', methods=['POST'])
def add_command():
    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'status': 'error', 'message': 'Missing command'}), 400
    command_text = data['command']
    with lock:
        commands.append(command_text)
    return jsonify({'status': 'success', 'command': command_text})

@app.route('/get_logs', methods=['GET'])
def get_logs():
    with lock:
        logs = list(device_logs)
    return jsonify({'logs': logs})

@app.route('/get_status', methods=['GET'])
def get_status():
    with lock:
        status_copy = dict(device_status)
    return jsonify({'status': status_copy})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)