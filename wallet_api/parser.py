import pandas as pd
import os
import requests

# Fonction pour récupérer le prix actuel d'un token à partir de l'API Dexscreener
def get_token_price(pair_addresses):
    url = f"https://api.dexscreener.io/latest/dex/tokens/{pair_addresses}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["pairs"] is not None:
            # Assumer que le prix est dans la première paire retournée
            price = data['pairs'][0]['priceUsd']
            return float(price)
        else:
            print(f"{pair_addresses} dex pairs not found")
    else:
        print("Error reading price")
    return None

# Fonction pour calculer le PnL total et générer un résumé des trades à partir d'un fichier CSV
def calculate_pnl_and_generate_summary(file_path, output_folder):
    # Charger les données CSV
    df = pd.read_csv(file_path)
    activity_types = ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"]
    df = df[df['activity_type'].isin(activity_types)]

    # Filtrer les transactions impliquant le token So11111111111111111111111111111111111111112
    Sola = 'So11111111111111111111111111111111111111112'
    df_token = df[(df['token1'] == Sola) | (df['token2'] == Sola)].copy()

    # Convertir les montants en fonction des décimales
    df_token.loc[:, 'amount1'] = df_token['amount1'] / (10 ** df_token['decimal1'])
    df_token.loc[:, 'amount2'] = df_token['amount2'] / (10 ** df_token['decimal2'])

    # Inverser l'ordre des lignes
    df_token = df_token.iloc[::-1].reset_index(drop=True)

    # Initialiser les compteurs pour le realized et unrealized PNL pour chaque token
    pnl_tracker = {}

    # Parcourir chaque transaction
    for index, row in df_token.iterrows():
        token1 = row['token1']  # vendre
        token2 = row['token2']  # achat
        amount1 = row['amount1']  # vendre
        amount2 = row['amount2']  # achat
        date = row['block_time']  # Assurer qu'il y a une colonne 'timestamp' dans le CSV

        if token1 == Sola:
            if token2 not in pnl_tracker:  # Premier achat
                pnl_tracker[token2] = {
                    'realized': 0, 'unrealized': 0, 'Sol_investi': 0, 'Sol_retiré': 0, 'balance': 0,
                    'trade_count': 0, 'first_trade_date': date, 'last_trade_date': date
                }
            pnl_tracker[token2]['Sol_investi'] += amount1
            pnl_tracker[token2]['balance'] += amount2
            pnl_tracker[token2]['last_trade_date'] = date
            pnl_tracker[token2]['trade_count'] += 1
        else:
            if token1 not in pnl_tracker:  # Vente sans achat
                pnl_tracker[token1] = {
                    'realized': 0, 'unrealized': 0, 'Sol_investi': 0, 'Sol_retiré': 0, 'balance': 0,
                    'trade_count': 0, 'first_trade_date': date, 'last_trade_date': date
                }
            pnl_tracker[token1]['Sol_retiré'] += amount2
            pnl_tracker[token1]['balance'] -= amount1
            pnl_tracker[token1]['last_trade_date'] = date
            pnl_tracker[token1]['trade_count'] += 1

    # Calculer le PnL réalisé pour chaque token
    for token, pnl in pnl_tracker.items():
        if pnl['Sol_investi'] > 0 and pnl['Sol_retiré'] == 0 and pnl['balance'] > 0:
            pnl['realized'] = 0  # Ne pas calculer le PnL réalisé
        elif pnl['Sol_investi'] > 0 and pnl['Sol_retiré'] == 0 and pnl['balance'] == 0:
            pnl['realized'] = -pnl['Sol_investi']  # Pertes totales car tout a été perdu
        else:
            pnl['realized'] = pnl['Sol_retiré'] - pnl['Sol_investi']

    # Récupérer les prix actuels des tokens non vendus pour calculer le PnL non réalisé
    for token, pnl in pnl_tracker.items():
        if pnl['balance'] > 0:
            price = get_token_price(token)
            if price is not None:
                pnl['unrealized'] = pnl['balance'] * price

    # Créer un DataFrame pour le résumé des trades
    summary_data = []
    for token, pnl in pnl_tracker.items():
        summary_data.append({
            'Token': token,
            'Sol_investi': pnl['Sol_investi'],
            'Sol_retiré': pnl['Sol_retiré'],
            'Balance': pnl['balance'],
            'Nombre de trades': pnl['trade_count'],
            'Date du premier trade': pnl['first_trade_date'],
            'Date du dernier trade': pnl['last_trade_date'],
            'PnL réalisé': pnl['realized'],
            'PnL non réalisé': pnl['unrealized']
        })

    summary_df = pd.DataFrame(summary_data)

    # Enregistrer le résumé dans un fichier CSV
    address = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(output_folder, f"{address}_summary.csv")
    summary_df.to_csv(output_file, index=False)

    # Calculer le PnL total
    total_realized_pnl = sum(pnl['realized'] for pnl in pnl_tracker.values())
    total_unrealized_pnl = sum(pnl['unrealized'] for pnl in pnl_tracker.values())
    return total_realized_pnl,total_unrealized_pnl

# Dossier contenant les fichiers CSV
input_folder = './wallet_api/toProcess/'
output_folder = './wallet_api/processed/'

# Créer le dossier 'processed' s'il n'existe pas
os.makedirs(output_folder, exist_ok=True)

# Initialiser un dictionnaire pour stocker les PnL totaux par adresse
address_pnls = {}

# Parcourir les fichiers CSV dans le dossier
for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_folder, filename)
        address = filename.split('.')[0]  # Utiliser le nom du fichier (sans extension) comme adresse
        total_realized_pnl, total_unrealized_pnl = calculate_pnl_and_generate_summary(file_path, output_folder)
        address_pnls[address] = total_realized_pnl, total_unrealized_pnl

# Afficher les PnL totaux pour chaque adresse
for address, total_pnl in address_pnls.items():
    print(f"Adresse: {address}")
    print(f"  PnL relized (sol): {total_pnl[0]}\n")
    print(f"  PnL unrelized (usd): {total_pnl[1]}\n")
