import multiprocessing
import time

# Fonction qui ajoute des éléments à la queue
def producer(queue):
    for i in range(10):
        print(f"Producteur ajoute: {i}")
        queue.put(i)
        time.sleep(1)  # Simuler un délai

# Fonction qui retire des éléments de la queue
def consumer(queue):
    while True:
        item = queue.get()  # Attend jusqu'à ce qu'un élément soit disponible
        print(f"Consommateur retire: {item}")
        if item == "FIN":
            break
        time.sleep(2)  # Simuler un traitement

if __name__ == "__main__":
    queue = multiprocessing.Queue()

    # Création des processus
    producer_process = multiprocessing.Process(target=producer, args=(queue,))
    consumer_process = multiprocessing.Process(target=consumer, args=(queue,))

    # Démarrage des processus
    producer_process.start()
    consumer_process.start()

    # Attendre que le producteur termine
    producer_process.join()

    # Ajouter un indicateur de fin pour arrêter le consommateur
    queue.put("FIN")

    # Attendre que le consommateur termine
    consumer_process.join()
