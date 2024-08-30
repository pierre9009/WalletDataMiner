# price_utils.py
import json
import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from config import SOL_PRICE_CACHE_FILE
from logger import setup_logger
from file_utils import round_to_nearest_hour, arrondir_heure_plus_proche

logger = setup_logger()

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
    
    logger.debug(f"Fetching SOL price for {dt_str}")
    sol_data = yf.download('SOL-USD', start=dt, end=dt + timedelta(hours=1), interval='1h', progress=False)
    if not sol_data.empty:
        price = sol_data.iloc[0]['Close']
        price_cache[dt_str] = price
        save_sol_price_cache(price_cache)  # Save the updated cache
        logger.debug(f"Added new SOL price for {dt_str}: ${price}")
        return price
    elif retries > 0:
        logger.warning(f"No data found for {dt}, retrying with {retries - 1} retries left...")
        return get_sol_price_at_time(dt - timedelta(hours=1), price_cache, retries - 1)
    else:
        logger.error(f"Failed to retrieve SOL price for {dt} after multiple attempts.")
        raise ValueError(f"Failed to retrieve SOL price for {dt} after multiple attempts.")

def get_token_prices(tokens, price_cache):
    recovered = 0
    prices = {}
    sol_price = get_sol_price_at_time(arrondir_heure_plus_proche(datetime.now()-timedelta(hours=1)), price_cache)

    for token in tokens:
        # Essayer d'abord avec Pump Fun
        url = f"https://frontend-api.pump.fun/candlesticks/{token}?offset=0&limit=1&timeframe=1"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if data and len(data) > 0:
                close_price = data[0].get('close', 0)
                prices[token] = close_price * sol_price
                recovered += 1
                continue  # Passer au token suivant si réussi
        except (requests.RequestException, ValueError) as e:
            logger.warning(f"Error requesting price for token {token} from Pump Fun: {e}")

        # Si Pump Fun échoue, essayer avec Jupiter
        jupiter_url = f"https://price.jup.ag/v6/price?ids={token}&vsToken=USDC"
        try:
            response = requests.get(jupiter_url, timeout=5)
            response.raise_for_status()
            data = response.json()
            if 'data' in data and token in data['data']:
                price = float(data['data'][token]['price'])
                prices[token] = price
                recovered += 1
            else:
                logger.warning(f"No price data found for token {token} from Jupiter")
        except (requests.RequestException, ValueError) as e:
            logger.warning(f"Error requesting price for token {token} from Jupiter: {e}")

    logger.info(f"Tokens price recovered: {recovered} over {len(tokens)}")
    return prices