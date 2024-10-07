# Utiliser une image de base Python
FROM python:3.11

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de l'application dans le conteneur
COPY . /app

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Définir la commande à exécuter lors du démarrage du conteneur
CMD ["python", "process_wallet.py"]
