from flask import Flask, jsonify
import subprocess
import os
import redis
import psutil  # Utilisé pour vérifier si le processus est en cours d'exécution
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Configuration de la connexion Redis (serveur maître)
redis_host = '82.67.116.111'  # Remplace par l'IP de ton serveur maître
redis_port = 6354
redis_queue_name = 'wallet_addresses'

# Initialiser la connexion Redis
r = redis.Redis(host=redis_host, port=redis_port, db=0, password=os.getenv('PASSWORD_REDIS_SERVER'))

app = Flask(__name__)

def is_process_running(process_name):
    """Vérifie si un processus est déjà en cours d'exécution"""
    for proc in psutil.process_iter(['pid', 'name']):
        if process_name in proc.info['name']:
            return True
    return False

def stop_all_processes(process_name):
    """Arrête tous les processus exécutant un script spécifique"""
    stopped_processes = []
    
    # Parcourir tous les processus en cours d'exécution
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Vérifier si c'est un processus Python et si le script correspond
            if proc.info['name'] == 'python3' and len(proc.info['cmdline']) > 1 and process_name in proc.info['cmdline'][1]:
                print(f"Arrêt du processus PID {proc.info['pid']} exécutant {proc.info['cmdline'][1]}")
                proc.terminate()  # Terminer le processus
                stopped_processes.append(proc.info['pid'])  # Enregistrer le PID du processus terminé
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignorer les erreurs pour les processus qui ne sont plus disponibles
    
    return stopped_processes


@app.route('/start_processing', methods=['POST'])
def start_processing():
    process_script = './process_wallet.py'  # Nom du script de traitement
    log_file = './process_wallet.log'  # Fichier de log où écrire les logs du processus

    if is_process_running("process_wallet.py"):  # Vérifier si le processus est déjà en cours
        return jsonify({"status": "running", "message": "process_wallet.py is already running"})
    
    if os.path.exists(process_script):
        try:
            # Ouvrir un fichier pour rediriger les logs
            with open(log_file, 'a') as f:
                # Lancer process_wallet.py en arrière-plan, et rediriger stdout et stderr vers le fichier de log
                subprocess.Popen(['python3', process_script], stdout=f, stderr=f)
            
            return jsonify({"status": "started", "message": f"process_wallet.py launched, logs in {log_file}"})
        except Exception as e:
            return jsonify({"status": "error", "message": str(e)})
    else:
        return jsonify({"status": "error", "message": f"{process_script} not found"}), 404

@app.route('/status', methods=['GET'])
def get_status():
    """Vérifier l'état du processus et la taille de la queue Redis"""
    is_running = is_process_running("process_wallet.py")
    queue_size = r.llen(redis_queue_name)
    
    return jsonify({
        "process_running": is_running,
        "queue_size": queue_size
    })

@app.route('/stop_processing', methods=['POST'])
def stop_processing():
    """Arrêter tous les processus de 'process_wallet.py'"""
    stopped_processes = stop_all_processes("process_wallet.py")
    if stopped_processes:
        return jsonify({"status": "stopped", "stopped_processes": stopped_processes})
    else:
        return jsonify({"status": "not_found", "message": "No process_wallet.py processes were running"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
