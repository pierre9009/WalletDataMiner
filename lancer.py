import requests
import json
import time

# URL de base de l'API (remplacez par l'adresse IP réelle du Raspberry Pi)
BASE_URL = "http://192.168.1.186:5000"

# Exemple 1: Envoyer des adresses à traiter
def send_addresses():
    url = f"{BASE_URL}/process"
    addresses = ["CuvaikSrjiwvsBs8W51oRomA3vgjQdgSVxFgXLyhnKq5", "CuvaikSrjiwvsBs8W51oRomA3vgjQdgSVxFgXLyhnKq5", "address3"]
    payload = {"addresses": addresses}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Requête réussie:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

def send_addresses2():
    url = f"{BASE_URL}/process"
    addresses = ["address1", "CuvaikSrjiwvsBs8W51oRomA3vgjQdgSVxFgXLyhnKq5", "address3"]
    payload = {"addresses": addresses}
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        print("Requête réussie:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Exemple 2: Vérifier le statut du traitement
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
    send_addresses2()
    
    print("\nVérification du statut:")
    check_status()