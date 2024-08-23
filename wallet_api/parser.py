import pandas as pd
import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from tqdm import tqdm
from colorama import Fore, Style, init

# Initialiser colorama pour Windows
init(autoreset=True)

# Liste des adresses des tokens à exclure (stablecoins)
EXCLUDED_TOKENS = [
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB'
]

# Fonction pour arrondir le timestamp à l'heure près
def round_to_nearest_hour(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return datetime(dt.year, dt.month, dt.day, dt.hour)

# Fonction pour récupérer le prix du SOL à une date et heure donnée en utilisant un cache
def get_sol_price_at_time(dt, price_cache):
    if dt in price_cache:
        return price_cache[dt]
    else:
        with open(os.devnull, 'w') as f:
            sol_data = yf.download('SOL-USD', start=dt, end=dt + timedelta(hours=1), interval='1h', progress=False)
        if not sol_data.empty:
            price = sol_data.iloc[0]['Close']
            price_cache[dt] = price
            return price
        else:
            return None

# Fonction pour récupérer le prix actuel d'un token à partir de l'API Dexscreener
def get_token_price(pair_addresses):
    url = f"https://api.dexscreener.io/latest/dex/tokens/{pair_addresses}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data["pairs"] is not None:
            price = data['pairs'][0]['priceUsd']
            return float(price)
    else:
        print("Error reading price")
    return None

# Fonction pour calculer le PnL total et générer un résumé des trades à partir d'un fichier CSV
def calculate_pnl_and_generate_summary(file_path, output_folder):
    df = pd.read_csv(file_path)
    activity_types = ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"]
    df = df[df['activity_type'].isin(activity_types)]
    Sola = 'So11111111111111111111111111111111111111112'
    df_token = df[(df['token1'] == Sola) | (df['token2'] == Sola)].copy()

    df_token.loc[:, 'amount1'] = df_token['amount1'] / (10 ** df_token['decimal1'])
    df_token.loc[:, 'amount2'] = df_token['amount2'] / (10 ** df_token['decimal2'])
    df_token = df_token.iloc[::-1].reset_index(drop=True)

    pnl_tracker = {}
    price_cache = {}

    for index, row in df_token.iterrows():
        token1 = row['token1']
        token2 = row['token2']
        amount1 = row['amount1']
        amount2 = row['amount2']
        timestamp = row['block_time']
        dt = round_to_nearest_hour(timestamp)

        if token1 in EXCLUDED_TOKENS or token2 in EXCLUDED_TOKENS:
            continue

        sol_price_at_time = get_sol_price_at_time(dt, price_cache)

        if sol_price_at_time is None:
            continue

        usd_investi = amount1 * sol_price_at_time if token1 == Sola else 0
        usd_retiré = amount2 * sol_price_at_time if token2 == Sola else 0

        if token1 == Sola:
            if token2 not in pnl_tracker:
                pnl_tracker[token2] = {
                    'realized': 0, 'unrealized': 0, 'usd_investi': 0, 'usd_retiré': 0, 'balance': 0,
                    'trade_count': 0, 'first_trade_date': dt, 'last_trade_date': dt
                }
            pnl_tracker[token2]['usd_investi'] += usd_investi
            pnl_tracker[token2]['balance'] += amount2
            pnl_tracker[token2]['last_trade_date'] = dt
            pnl_tracker[token2]['trade_count'] += 1
        else:
            if token1 not in pnl_tracker:
                pnl_tracker[token1] = {
                    'realized': 0, 'unrealized': 0, 'usd_investi': 0, 'usd_retiré': 0, 'balance': 0,
                    'trade_count': 0, 'first_trade_date': dt, 'last_trade_date': dt
                }
            pnl_tracker[token1]['usd_retiré'] += usd_retiré
            pnl_tracker[token1]['balance'] -= amount1
            pnl_tracker[token1]['last_trade_date'] = dt
            pnl_tracker[token1]['trade_count'] += 1

    for token, pnl in pnl_tracker.items():
        if pnl['usd_investi'] > 0 and pnl['usd_retiré'] == 0 and pnl['balance'] > 0:
            pnl['realized'] = 0
        else:
            pnl['realized'] = pnl['usd_retiré'] - pnl['usd_investi']

    for token, pnl in pnl_tracker.items():
        if pnl['balance'] > 0:
            price = get_token_price(token)
            if price is not None:
                pnl['unrealized'] = pnl['balance'] * price

    summary_data = []
    for token, pnl in pnl_tracker.items():
        summary_data.append({
            'Token': token,
            'USD investi': pnl['usd_investi'],
            'USD retiré': pnl['usd_retiré'],
            'Balance': pnl['balance'],
            'Nombre de trades': pnl['trade_count'],
            'Date du premier trade': pnl['first_trade_date'],
            'Date du dernier trade': pnl['last_trade_date'],
            'PnL réalisé (USD)': pnl['realized'],
            'PnL non réalisé (USD)': pnl['unrealized']
        })

    summary_df = pd.DataFrame(summary_data)

    address = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(output_folder, f"{address}_summary.csv")
    summary_df.to_csv(output_file, index=False)

    total_realized_pnl = sum(pnl['realized'] for pnl in pnl_tracker.values())
    total_unrealized_pnl = sum(pnl['unrealized'] for pnl in pnl_tracker.values())
    return total_realized_pnl, total_unrealized_pnl

input_folder = './wallet_api/toProcess/'
output_folder = './wallet_api/processed/'

os.makedirs(output_folder, exist_ok=True)
address_pnls = {}

# Calculer le nombre total de transactions pour toutes les barres de progression
total_transactions = sum([len(pd.read_csv(os.path.join(input_folder, f)).index) 
                          for f in os.listdir(input_folder) if f.endswith('.csv')])

# Initialiser la barre de progression globale
pbar = tqdm(total=total_transactions, desc="Processing all transactions", unit="tx")

for filename in os.listdir(input_folder):
    if filename.endswith('.csv'):
        file_path = os.path.join(input_folder, filename)
        address = filename.split('.')[0]
        
        # Calculer le PnL pour l'adresse
        total_realized_pnl, total_unrealized_pnl = calculate_pnl_and_generate_summary(file_path, output_folder)
        address_pnls[address] = total_realized_pnl, total_unrealized_pnl
        
        # Mettre à jour la barre de progression globale
        pbar.update(len(pd.read_csv(file_path).index))

pbar.close()

# Affichage des PnL par adresse avec coloration
print(Fore.GREEN + Style.BRIGHT + "\nRésultats du PnL par adresse:\n" + "-"*50 + "\n")
for address, total_pnl in address_pnls.items():
    color_realized = Fore.GREEN if total_pnl[0] >= 0 else Fore.RED
    color_unrealized = Fore.GREEN if total_pnl[1] >= 0 else Fore.RED
    
    print(Fore.CYAN + Style.BRIGHT + f"Adresse: {address}")
    print(color_realized + f"  PnL réalisé (USD): {total_pnl[0]}")
    print(color_unrealized + f"  PnL non réalisé (USD): {total_pnl[1]}")
    print(Fore.GREEN + "-"*50)
