import requests
import json
import time

# URL de base de l'API (remplacez par l'adresse IP réelle du Raspberry Pi)
BASE_URL = "http://192.168.1.18:5000"

# Envoyer des adresses à traiter
def send_addresses():
    url = f"{BASE_URL}/process"
    addresses = ["CuvaikSrjiwvsBs8W51oRomA3vgjQdgSVxFgXLyhnKq5", "address2", "address3"]
    payload = {"addresses": addresses}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Requête réussie:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Envoyer un deuxième ensemble d'adresses
def send_addresses2():
    url = f"{BASE_URL}/process"
    addresses = ["address4", "address5", "address6"]
    payload = {"addresses": addresses}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Requête réussie:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Démarrer le processus de traitement via l'API
def start_processing():
    url = f"{BASE_URL}/start_processing"
    
    response = requests.post(url)
    
    if response.status_code == 200:
        print("Traitement démarré avec succès:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Vérifier le statut du traitement
def check_status():
    url = f"{BASE_URL}/status"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Statut actuel:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Exécution des exemples
if __name__ == "__main__":
    print("Envoi des adresses:")
    send_addresses()
    time.sleep(2)

    print("\nDémarrage du processus de traitement:")
    start_processing()
    time.sleep(2)

    print("\nEnvoi de nouvelles adresses:")
    send_addresses2()
    time.sleep(2)

    print("\nVérification du statut:")
    check_status()

    time.sleep(20)
    send_addresses()
