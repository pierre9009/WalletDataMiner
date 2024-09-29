from flask import Flask, request, jsonify
from config import WALLET_ADDRESSES_FILE, PROCESS_SCRIPT
import subprocess
import os
import fcntl

app = Flask(__name__)

def append_addresses_to_file(addresses):
    with open(WALLET_ADDRESSES_FILE, 'a') as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # Verrou exclusif pour écrire dans le fichier
        for address in addresses:
            f.write(f"{address}\n")
        fcntl.flock(f, fcntl.LOCK_UN)  # Libérer le verrou

@app.route('/process', methods=['POST'])
def process_addresses():
    data = request.json
    addresses = data.get('addresses', [])
    
    if not addresses:
        return jsonify({"status": "error", "message": "No addresses provided"}), 400

    # Enregistrer les adresses dans le fichier
    append_addresses_to_file(addresses)
    
    return jsonify({"status": "processing", "address_count": len(addresses)})

@app.route('/start_processing', methods=['POST'])
def start_processing():
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
    # Implémentation basique de vérification d'état (à améliorer selon votre logique)
    if os.path.exists(WALLET_ADDRESSES_FILE):
        with open(WALLET_ADDRESSES_FILE, 'r') as f:
            fcntl.flock(f, fcntl.LOCK_SH)  # Verrou pour lecture partagée
            remaining_addresses = [line.strip() for line in f if line.strip()]
            fcntl.flock(f, fcntl.LOCK_UN)  # Libérer le verrou

        if remaining_addresses:
            return jsonify({"status": "processing", "remaining_addresses": len(remaining_addresses)})
        else:
            return jsonify({"status": "idle", "message": "No addresses left to process"})
    else:
        return jsonify({"status": "error", "message": f"{WALLET_ADDRESSES_FILE} not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
