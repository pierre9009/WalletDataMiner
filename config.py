# config.py
from datetime import datetime, timedelta

# Chemins des dossiers
INPUT_FOLDER = './toProcess/'
OUTPUT_FOLDER = './processed/'


# Configurations des tokens
EXCLUDED_TOKENS = {
    'EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v',  # USDC
    'Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB',  # USDT
    '7vfCXTUXx5WJV5JADk17DUJ4ksgau7utNKj4b963voxs'   # WETH
}

SOLANA_ADDRESSES = {
    'So11111111111111111111111111111111111111112', # WSOL
    'So11111111111111111111111111111111111111111' # SOL
}

# Fichier de cache
SOL_PRICE_CACHE_FILE = 'sol_price_cache.json'

# Paramètres de calcul
START_DATE = datetime.now() - timedelta(days=30)

# URLs des API
PUMP_FUN_API_URL = "https://frontend-api.pump.fun/candlesticks/{token}?offset=0&limit=1&timeframe=1"
JUPITER_API_URL = "https://price.jup.ag/v6/price?ids={token}&vsToken=USDC"
SOLSCAN_API_URL = "https://api-v2.solscan.io/v2/account/activity/dextrading?address={address}&page={{page}}&page_size=100"

# Autres paramètres solscan ou yfinance
REQUEST_TIMEOUT = 5
MAX_RETRIES = 3

#Time out de pump fun ou jupiter pour recuperer le prix des tokens (seconde)
API_TIMEOUT = 1

# Types d'activités à inclure dans le calcul PnL
INCLUDED_ACTIVITY_TYPES = ["ACTIVITY_TOKEN_SWAP", "ACTIVITY_AGG_TOKEN_SWAP"]
PROCESS_SCRIPT = './process_wallet.py'

#max transactions à crawl depuis solscan
MAX_TRANSACTIONS = 3000

#Progesql (port 5432)
IP_WALLET_DB = "db.pierreminh.com"
DB_WALLET = "wallet_db"
USER_WALLET_DB = "pierre"

#Redis
REDIS_HOST = 'redis.pierreminh.com'
REDIS_PORT = 6354
REDIS_QUEUE_NAME = 'wallet_addresses'