import pandas as pd
import os
import requests
import logging
from datetime import datetime, timedelta
import yfinance as yf
from colorama import Fore, Style, init
import json

# Initialize colorama for Windows
init(autoreset=True)

# Custom colored logger
class ColoredLogger(logging.Logger):
    COLOR_MAP = {
        'DEBUG': Fore.BLUE,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT
    }

    def __init__(self, name):
        super().__init__(name)

    def _log(self, level, msg, args, exc_info=None, extra=None):
        color = self.COLOR_MAP.get(logging.getLevelName(level), '')
        msg = f"{color}{msg}{Style.RESET_ALL}"
        super()._log(level, msg, args, exc_info, extra)

logging.setLoggerClass(ColoredLogger)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

EXCLUDED_TOKENS = {
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  # USDT
    '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs'   # WETH
}

# Solana addresses to include in transactions
SOLANA_ADDRESSES = {
    'So11111111111111111111111111111111111111112',
    'So11111111111111111111111111111111111111111'
}
SOL_PRICE_CACHE_FILE = 'sol_price_cache.json'

def round_to_nearest_hour(timestamp):
    dt = datetime.fromtimestamp(timestamp)
    return datetime(dt.year, dt.month, dt.day, dt.hour)

def load_sol_price_cache():
    if os.path.exists(SOL_PRICE_CACHE_FILE):
        with open(SOL_PRICE_CACHE_FILE, 'r') as f:
            cache = json.load(f)
        logger.info(f"Loaded SOL price cache with {len(cache)} entries")
        return cache
    logger.info("No existing SOL price cache found. Starting with empty cache.")
    return {}

def save_sol_price_cache(cache):
    with open(SOL_PRICE_CACHE_FILE, 'w') as f:
        json.dump(cache, f)
    logger.info(f"Saved SOL price cache with {len(cache)} entries")

def get_sol_price_at_time(dt, price_cache, retries=3):
    dt_str = dt.isoformat()
    if dt_str in price_cache:
        logger.debug(f"SOL price for {dt_str} found in cache")
        return price_cache[dt_str]
    
    logger.info(f"Fetching SOL price for {dt_str}")
    sol_data = yf.download('SOL-USD', start=dt, end=dt + timedelta(hours=1), interval='1h', progress=False)
    if not sol_data.empty:
        price = sol_data.iloc[0]['Close']
        price_cache[dt_str] = price
        save_sol_price_cache(price_cache)  # Save the updated cache
        logger.info(f"Added new SOL price for {dt_str}: ${price}")
        return price
    elif retries > 0:
        logger.warning(f"No data found for {dt}, retrying with {retries - 1} retries left...")
        return get_sol_price_at_time(dt - timedelta(hours=1), price_cache, retries - 1)
    else:
        logger.error(f"Failed to retrieve SOL price for {dt} after multiple attempts.")
        raise ValueError(f"Failed to retrieve SOL price for {dt} after multiple attempts.")

def get_token_price(pair_addresses):
    url = f"https://api.dexscreener.io/latest/dex/tokens/{pair_addresses}"
    try:
        response = requests.get(url, timeout=3)
        response.raise_for_status()
        data = response.json()
        if data.get("pairs"):
            price = float(data['pairs'][0]['priceUsd'])
            return price
    except (requests.RequestException, ValueError) as e:
        logger.warning(f"Error requesting {pair_addresses} through dexscreener: {e}")
    return None

def process_transaction(row, price_cache, pnl_tracker):
    token1, token2 = row['token1'], row['token2']
    amount1, amount2 = row['amount1'], row['amount2']
    dt = round_to_nearest_hour(row['block_time'].timestamp())

    if token1 in EXCLUDED_TOKENS or token2 in EXCLUDED_TOKENS:
        logger.debug(f"Skipping transaction with excluded token(s): {token1}, {token2}")
        return

    if token1 not in SOLANA_ADDRESSES and token2 not in SOLANA_ADDRESSES:
        logger.debug(f"Skipping non-Solana transaction: {token1}, {token2}")
        return

    sol_price_at_time = get_sol_price_at_time(dt, price_cache)
    if sol_price_at_time is None:
        logger.warning(f"Unable to process transaction due to missing SOL price for {dt}")
        return

    usd_invested = amount1 * sol_price_at_time if token1 in SOLANA_ADDRESSES else 0
    usd_withdrawn = amount2 * sol_price_at_time if token2 in SOLANA_ADDRESSES else 0

    target_token = token2 if token1 in SOLANA_ADDRESSES else token1
    if target_token not in pnl_tracker:
        pnl_tracker[target_token] = {
            'realized': 0, 'unrealized': 0, 'usd_invested': 0, 'usd_withdrawn': 0, 'balance': 0,
            'trade_count': 0, 'first_trade_date': dt, 'last_trade_date': dt
        }

    pnl = pnl_tracker[target_token]
    if token1 in SOLANA_ADDRESSES:
        pnl['usd_invested'] += usd_invested
        pnl['balance'] += amount2
        logger.debug(f"Processed buy transaction for {target_token}: ${usd_invested} invested, balance: {pnl['balance']}")
    else:
        pnl['usd_withdrawn'] += usd_withdrawn
        pnl['balance'] -= amount1
        logger.debug(f"Processed sell transaction for {target_token}: ${usd_withdrawn} withdrawn, balance: {pnl['balance']}")

    pnl['last_trade_date'] = dt
    pnl['trade_count'] += 1

def calculate_pnl_and_generate_summary(file_path, output_folder, start_date=None):
    logger.info(f"Starting PnL calculation for file: {file_path}")
    df = pd.read_csv(file_path)
    df = df[df['activity_type'].isin(["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"])]
    df['block_time'] = pd.to_datetime(df['block_time'], unit='s')

    if start_date:
        df = df[df['block_time'] >= start_date]
        logger.info(f"Filtered transactions from {start_date}, {len(df)} transactions remaining")

    df['amount1'] = df['amount1'] / (10 ** df['decimal1'])
    df['amount2'] = df['amount2'] / (10 ** df['decimal2'])
    df = df.iloc[::-1].reset_index(drop=True)

    pnl_tracker = {}
    price_cache = load_sol_price_cache()

    logger.info(f"Processing {len(df)} transactions")
    for _, row in df.iterrows():
        process_transaction(row, price_cache, pnl_tracker)

    logger.info("Calculating realized PnL")
    for token, pnl in pnl_tracker.items():
        if pnl['usd_invested'] > 0 and pnl['usd_withdrawn'] == 0 and pnl['balance'] > 0:
            pnl['realized'] = 0
        else:
            pnl['realized'] = pnl['usd_withdrawn'] - pnl['usd_invested']
        logger.debug(f"Realized PnL for {token}: ${pnl['realized']}")

    logger.info("Calculating unrealized PnL")
    for token, pnl in pnl_tracker.items():
        if pnl['balance'] > 0:
            price = get_token_price(token)
            if price is not None:
                pnl['unrealized'] = pnl['balance'] * price
                logger.debug(f"Unrealized PnL for {token}: ${pnl['unrealized']}")
            else:
                pnl['unrealized'] = 0

    summary_data = [
            {
                'Token': token,
                'USD invested': pnl['usd_invested'],
                'USD withdrawn': pnl['usd_withdrawn'],
                'Balance': pnl['balance'],
                'Number of trades': pnl['trade_count'],
                'First trade date': pnl['first_trade_date'],
                'Last trade date': pnl['last_trade_date'],
                'Realized PnL (USD)': pnl['realized'],
                'Unrealized PnL (USD)': pnl['unrealized']
            }
            for token, pnl in pnl_tracker.items()
        ]

    summary_df = pd.DataFrame(summary_data)
    address = os.path.splitext(os.path.basename(file_path))[0]
    output_file = os.path.join(output_folder, f"{address}_summary.csv")
    summary_df.to_csv(output_file, index=False)
    logger.info(f"Saved summary to {output_file}")

    total_realized_pnl = sum(pnl['realized'] for pnl in pnl_tracker.values())
    total_unrealized_pnl = sum(pnl['unrealized'] for pnl in pnl_tracker.values())
    logger.info(f"Total Realized PnL: ${total_realized_pnl}, Total Unrealized PnL: ${total_unrealized_pnl}")
    return total_realized_pnl, total_unrealized_pnl
    
def clear_input_folder(folder_path):
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
def main():
    logger.info("Starting PnL calculation process")
    input_folder = './wallet_api/toProcess/'
    output_folder = './wallet_api/processed/'
    os.makedirs(output_folder, exist_ok=True)

    start_date = datetime.now() - timedelta(days=7)
    logger.info(f"Using start date: {start_date}")
    address_pnls = {}

    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            address = filename.split('.')[0]
            logger.info(f"Processing file for address: {address}")
            total_realized_pnl, total_unrealized_pnl = calculate_pnl_and_generate_summary(file_path, output_folder, start_date)
            address_pnls[address] = (total_realized_pnl, total_unrealized_pnl)
            logger.info("--------------------------------------------------------------------------------------")

    print(Fore.GREEN + Style.BRIGHT + "\nPnL Results by Address:\n" + "-"*50 + "\n")
    for address, (realized_pnl, unrealized_pnl) in address_pnls.items():
        print(Fore.CYAN + Style.BRIGHT + f"Address: {address}")
        print(f"{Fore.GREEN if realized_pnl >= 0 else Fore.RED}  Realized PnL (USD): {realized_pnl}")
        print(f"{Fore.GREEN if unrealized_pnl >= 0 else Fore.RED}  Unrealized PnL (USD): {unrealized_pnl}")
        print(Fore.GREEN + "-"*50)

    clear_input_folder(input_folder)
    logger.info("PnL calculation process completed")

if __name__ == "__main__":
    main()
