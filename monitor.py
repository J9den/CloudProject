import time
import json
import requests
import os
from datetime import datetime

# Configuration
DATA_FILE = 'instances.json'
LOG_FILE = 'monitor.log'
API_URL = "http://localhost:5000/api"


def log_message(msg):
    """Write log message to file and console"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(LOG_FILE, 'a') as f:
        f.write(f'[{timestamp}] {msg}\n')
    print(f'[{timestamp}] {msg}')


def load_data():
    """Load date from JSON file"""
    if not os.path.exists(DATA_FILE):
        return {'instances': []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data):
    """Save instances data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def check_and_stop():
    """Check all running instances and stop if conditions are met"""
    data = load_data()
    changed = False

    for inst in data['instances']:
        if inst['status'] != 'running':
            continue

        now = time.time()
        reason = None

        # Rule 1: Runtime limit (1 minutes for testing)
        runtime = now - inst.get('start_time', inst['created_at'])
        if runtime > 60:  # 1 minutes = 60 seconds
            reason = f'Runtime exceeded 1 minutes ({int(runtime / 60)} minutes)'

        # Rule 2: User quota exceeded (max 2 instances per user)
        if not reason:
            user = inst['user']
            user_running = 0
            for i in data['instances']:
                if i['user'] == user and i['status'] == 'running':
                    user_running += 1

            if user_running > 2:
                reason = f'User {user} quota exceeded (max 2, current {user_running})'

        # Stop if any rule triggered
        if reason:
            try:
                # Call API to stop instance
                resp = requests.post(f"{API_URL}/stop/{inst['id']}")

                log_message(f'Stopped instance {inst["name"]} ({inst["id"]}) - Reason: {reason}')

                # Add：stop time
                stop_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                inst['status'] = 'stopped'
                inst['stopped_at'] = stop_time
                inst['stop_reason'] = reason

                changed = True

            except Exception as e:
                log_message(f'API call failed: {str(e)}')

    if changed:
        save_data(data)


def main():
    """Main monitoring loop"""
    log_message('Monitoring service started')
    cycle = 0

    try:
        while True:  # Means do the cycle forever, we need cycle calculater to make sure that monitor is working.
            cycle += 1
            log_message(f'Check cycle {cycle} started')

            check_and_stop()

            log_message(f'Check completed, waiting 30 seconds')
            time.sleep(30)  # Check every 30 seconds

    except KeyboardInterrupt:
        log_message('Monitoring service stopped')


if __name__ == '__main__':
    main()