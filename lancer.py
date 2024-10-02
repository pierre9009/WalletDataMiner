import requests
import json
import time

# URL de base de l'API (remplace par l'adresse IP réelle du Raspberry Pi esclave)
BASE_URL = "http://192.168.1.18:5000"

# Démarrer le processus de traitement via l'API (uniquement si le script n'est pas en cours d'exécution)
def start_processing():
    url = f"{BASE_URL}/start_processing"
    
    response = requests.post(url)
    
    if response.status_code == 200:
        print("Démarrage du processus de traitement:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Vérifier le statut du traitement (vérifie si le processus est en cours et la taille de la queue Redis)
def check_status():
    url = f"{BASE_URL}/status"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        print("Statut actuel:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Arrêter tous les processus de traitement via l'API
def stop_processing():
    url = f"{BASE_URL}/stop_processing"
    
    response = requests.post(url)
    
    if response.status_code == 200:
        print("Arrêt du processus de traitement:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Erreur: {response.status_code}")
        print(response.text)

# Exécution des tests
if __name__ == "__main__":

    print("\nArrêt du processus de traitement:")
    stop_processing()
    time.sleep(10)


    print("\nVérification de l'état du traitement avant le démarrage:")
    check_status()
    time.sleep(2)

    print("\nDémarrage du processus de traitement:")
    start_processing()
    time.sleep(5)

    print("\nVérification de l'état du traitement après le démarrage:")
    check_status()
    time.sleep(2)

    

    print("\nVérification de l'état du traitement après l'arrêt:")
    check_status()
