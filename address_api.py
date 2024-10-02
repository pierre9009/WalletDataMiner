from flask import Flask, jsonify
import subprocess
import os
import redis
import psutil  # Utilisé pour vérifier si le processus est en cours d'exécution

# Configuration de la connexion Redis (serveur maître)
redis_host = '82.67.116.111'  # Remplace par l'IP de ton serveur maître
redis_port = 6354
redis_queue_name = 'wallet_addresses'

# Initialiser la connexion Redis
r = redis.Redis(host=redis_host, port=redis_port, db=0, password = os.getenv('PASSWORD_REDIS_SERVER'))

app = Flask(__name__)

def is_process_running(process_name):
    """Vérifie si un processus est déjà en cours d'exécution"""
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return True
    return False

@app.route('/start_processing', methods=['POST'])
def start_processing():
    process_script = 'process_wallet.py'  # Nom du script de traitement
    
    if is_process_running("python3"):  # Vérifier si le processus est déjà en cours
        return jsonify({"status": "running", "message": "process_wallet.py is already running"})
    
    if os.path.exists(process_script):
        try:
            # Lancer process_wallet.py en arrière-plan
            subprocess.Popen(['python3', process_script])
            return jsonify({"status": "started", "message": "process_wallet.py launched"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": f"{process_script} not found"}), 404

@app.route('/status', methods=['GET'])
def get_status():
    """Vérifier l'état du processus et la taille de la queue Redis"""
    is_running = is_process_running("python3")
    queue_size = r.llen(redis_queue_name)
    
    return jsonify({
        "process_running": is_running,
        "queue_size": queue_size
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
