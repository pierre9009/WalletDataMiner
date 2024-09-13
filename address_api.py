#address_api

from flask import Flask, request, jsonify
import subprocess

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_addresses():
    data = request.json
    addresses = data.get('addresses', [])
    
    # Enregistrez les adresses dans un fichier
    with open('addresses_to_process.txt', 'w') as f:
        for address in addresses:
            f.write(f"{address}\n")
    
    # Lancez le script de traitement en arrière-plan
    subprocess.Popen(["python", "main.py"])
    
    return jsonify({"status": "processing", "address_count": len(addresses)})

@app.route('/status', methods=['GET'])
def get_status():
    # Vérifiez l'état du traitement (à implémenter selon votre logique)
    # Par exemple, vous pourriez vérifier si un fichier de résultats existe
    
    return jsonify({"status": "in_progress"})  # ou "completed" avec les résultats

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)