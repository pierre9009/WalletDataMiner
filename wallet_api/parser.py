import pandas as pd
import os

# Fonction pour calculer le PnL total à partir d'un fichier CSV
def calculate_pnl(file_path):
    # Charger les données CSV
    df = pd.read_csv(file_path)

    # Filtrer les transactions impliquant le token So11111111111111111111111111111111111111112
    Sola = 'So11111111111111111111111111111111111111112'
    df_token = df[(df['token1'] == Sola) | (df['token2'] == Sola)]

    # Convertir les montants en fonction des décimales
    df_token['amount1'] = df_token['amount1'] / (10 ** df_token['decimal1'])
    df_token['amount2'] = df_token['amount2'] / (10 ** df_token['decimal2'])

    # Inverser l'ordre des lignes
    df_token = df_token[::-1]

    # Initialiser les compteurs pour le realized et unrealized PNL pour chaque token
    pnl_tracker = {}

    # Parcourir chaque transaction
    for index, row in df_token.iterrows():
        token1 = row['token1']  # vendre
        token2 = row['token2']  # achat
        amount1 = row['amount1']  # vendre
        amount2 = row['amount2']  # achat

        if token1 == Sola:
            if token2 not in pnl_tracker:  # Premier achat
                pnl_tracker[token2] = {'realized': 0, 'unrealized': 0, 'Sol_investi': 0, 'Sol_retiré': 0, 'balance': 0}
            pnl_tracker[token2]['Sol_investi'] += amount1
            pnl_tracker[token2]['balance'] += amount2
        else:
            if token1 not in pnl_tracker:  # Vente sans achat
                pnl_tracker[token1] = {'realized': 0, 'unrealized': 0, 'Sol_investi': 0, 'Sol_retiré': 0, 'balance': 0}
            pnl_tracker[token1]['Sol_retiré'] += amount2
            pnl_tracker[token1]['balance'] -= amount1

    # Calculer le PnL réalisé pour chaque token
    for token in pnl_tracker:
        pnl_tracker[token]['realized'] = pnl_tracker[token]['Sol_retiré'] - pnl_tracker[token]['Sol_investi']

    # Calculer le PnL total
    total_realized_pnl = sum(pnl['realized'] for pnl in pnl_tracker.values())
    return total_realized_pnl

# Dossier contenant les fichiers CSV
folder_path = './wallet_api/toProcess/'

# Initialiser un dictionnaire pour stocker les PnL totaux par adresse
address_pnls = {}

# Parcourir les fichiers CSV dans le dossier
for filename in os.listdir(folder_path):
    if filename.endswith('.csv'):
        file_path = os.path.join(folder_path, filename)
        address = filename.split('.')[0]  # Utiliser le nom du fichier (sans extension) comme adresse
        total_pnl = calculate_pnl(file_path)
        address_pnls[address] = total_pnl

# Afficher les PnL totaux pour chaque adresse
for address, total_pnl in address_pnls.items():
    print(f"Adresse: {address}")
    print(f"  PnL total : {total_pnl}\n")
