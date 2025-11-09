from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory devices store: device_id -> device_info
devices = {}

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/devices', methods=['GET'])
def list_devices():
    return jsonify(list(devices.values())), 200

@app.route('/devices/<device_id>', methods=['GET'])
def get_device(device_id):
    d = devices.get(device_id)
    if not d:
        return jsonify({"error": "not found"}), 404
    return jsonify(d), 200

@app.route('/devices', methods=['POST'])
def create_device():
    data = request.get_json(force=True)
    device_id = str(data.get('id'))
    if not device_id:
        return jsonify({"error": "id required"}), 400
    devices[device_id] = data
    return jsonify(data), 201

@app.route('/devices/<device_id>', methods=['PUT'])
def update_device(device_id):
    data = request.get_json(force=True)
    devices[device_id] = data
    return jsonify(data), 200

@app.route('/devices/<device_id>', methods=['DELETE'])
def delete_device(device_id):
    if device_id in devices:
        del devices[device_id]
        return jsonify({"status": "deleted"}), 200
    return jsonify({"error": "not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8083)
