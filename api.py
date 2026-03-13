from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import time
from vm_controller import VMController
from docker_controller import DockerController

app = Flask(__name__)
CORS(app)  #Allow communication between the front end and the back end

vm_ctrl = VMController() #controller for VM
docker_ctrl = DockerController()# controller for Docker

DATA_FILE = 'instances.json'


def load_data():
    """Load date from JSON file"""
    if not os.path.exists(DATA_FILE):
        return {'instances': []}
    with open(DATA_FILE, 'r') as f:
        return json.load(f)


def save_data(data):
    """Save date to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@app.route('/api/create', methods=['POST'])
def create_instance():
    """Create instance"""
    data = request.json

    # Check the parameter
    required = ['name', 'type', 'os', 'cpu', 'memory', 'user']
    for field in required:
        if field not in data:
            return jsonify({'success': False, 'error': f'Lack the parameter: {field}'}), 400

    if data['type'] == 'vm':
        result = vm_ctrl.create(
            name=data['name'],
            os_type=data['os'],
            cpu=data['cpu'],
            memory=data['memory'],
            user=data['user']
        )
    else:  # container
        result = docker_ctrl.create(
            name=data['name'],
            image=data['os'],
            cpu=data['cpu'],
            memory=data['memory'],
            user=data['user']
        )

    if result['success']:
        # save to json
        db = load_data()
        instance = {
            'id': result['id'],
            'name': data['name'],
            'type': data['type'],
            'os': data['os'],
            'cpu': data['cpu'],
            'memory': data['memory'],
            'status': 'running',
            'user': data['user'],
            'created_at': result['created_at'],
            'start_time': result['created_at']
        }
        db['instances'].append(instance)
        save_data(db)

        return jsonify({
            'success': True,
            'instance_id': result['id'],
            'message': 'create successfully'
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error']
        }),


@app.route('/api/list', methods=['GET'])
def list_instances():
    """Get list of instances"""
    user = request.args.get('user')
    db = load_data()

    if user is not None:
        instances = []
        for i in db['instances']:
            if i['user'] == user:
                instances.append(i)
    else:
        instances = db['instances']

    return jsonify(instances)


@app.route('/api/stop/<instance_id>', methods=['POST'])
def stop_instance(instance_id):
    """Stop instance"""
    db = load_data()

    # find the target instance
    instance = None
    for i in db['instances']:
        if i['id'] == instance_id:
            instance = i
            break
    if instance is None:
        return jsonify({'success': False, 'error': 'Instance is not existing'})

    # stop the target
    if instance['type'] == 'vm':
        result = vm_ctrl.stop(instance_id)
    else:
        result = docker_ctrl.stop(instance_id)

    if result['success']:
        instance['status'] = 'stopped'
        save_data(db)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result['error']})


@app.route('/api/start/<instance_id>', methods=['POST'])
def start_instance(instance_id):
    """Start instance"""
    db = load_data()

    # Find target
    instance = None
    for i in db['instances']:
        if i['id'] == instance_id:
            instance = i
            break

    if instance is None:
        return jsonify({'success': False, 'error': 'Instance is not existing'})

    # start target
    if instance['type'] == 'vm':
        result = vm_ctrl.start(instance_id)
    else:
        result = docker_ctrl.start(instance_id)

    if result['success']:
        instance['status'] = 'running'
        instance['start_time'] = time.time()
        save_data(db)
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': result['error']})


"""Place for monitor
@app.route('/api/monitor', methods=['GET'])
def monitor_data():
    #for monitor
    db = load_data()

    total = len(db['instances'])
    running = sum(1 for i in db['instances'] if i['status'] == 'running')


    return jsonify({
        'total': total,
        'running': running,
        'stopped': total - running,
        'recent_stops': [] 
    })"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)