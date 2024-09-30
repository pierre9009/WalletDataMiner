#address_api.py
from flask import Flask, request, jsonify
from config import PROCESS_SCRIPT
import subprocess
from multiprocessing import Queue
import os
import fcntl

app = Flask(__name__)


@app.route('/process', methods=['POST'])
def process_addresses():
    data = request.json
    addresses = data.get('addresses', [])
    
    if not addresses:
        return jsonify({"status": "error", "message": "No addresses provided"}), 400

    # Ajouter les adresses à la queue partagée
    for address in addresses:
        address_queue.put(address)

    return jsonify({"status": "processing", "address_count": len(addresses)})

@app.route('/start_processing', methods=['POST'])
def start_processing():
    address_queue = Queue()
    if os.path.exists(PROCESS_SCRIPT):
        try:
            # Lancer process_wallet.py en arrière-plan
            subprocess.Popen(['python3', PROCESS_SCRIPT])
            return jsonify({"status": "started", "message": "process_wallet.py launched"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": f"{PROCESS_SCRIPT} not found"}), 404

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "queue_size", "remaining_addresses": address_queue.qsize()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
