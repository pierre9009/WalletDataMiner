from config import INPUT_FOLDER, OUTPUT_FOLDER, START_DATE, WALLET_ADDRESSES_FILE, SOLSCAN_API_URL
from logger import setup_logger
from price_utils import load_sol_price_cache, save_sol_price_cache, get_sol_price_at_time, get_token_prices
from pnl_calculation import process_transaction, calculate_unrealized_pnl, calculate_pnl_and_generate_summary
from file_utils import clear_input_folder
from get_trans import run_scraper
from toDatabase import toDatabase, connection_to_db, close_sql_connection
import os
import time
import fcntl

def read_addresses(file_path):
    with open(file_path, 'r') as f:
        fcntl.flock(f, fcntl.LOCK_SH)  # Verrou pour lecture partagée
        addresses = [line.strip() for line in f if line.strip()]
        fcntl.flock(f, fcntl.LOCK_UN)  # Libérer le verrou
    return addresses

def write_addresses(file_path, addresses):
    with open(file_path, 'w') as f:
        fcntl.flock(f, fcntl.LOCK_EX)  # Verrou exclusif pour écriture
        for address in addresses:
            f.write(f"{address}\n")
        fcntl.flock(f, fcntl.LOCK_UN)  # Libérer le verrou

def process_address(address, logger, connection, cursor):
    file_path = os.path.join(INPUT_FOLDER, f"{address}.csv")
    
    # Lancer le scraper pour récupérer les données
    logger.info(f"Starting scraper for address: {address}")
    run_scraper([address], logger)  # Appel à run_scraper pour chaque adresse

    if os.path.exists(file_path):
        logger.info(f"Processing file for address: {address}")
        metrics = calculate_pnl_and_generate_summary(logger, file_path, OUTPUT_FOLDER, START_DATE)

        # Afficher les métriques de trading
        logger.info(f"Trading metrics for {address}:")
        logger.info(f"Gross Profit: ${metrics['gross_profit']:.2f}")
        logger.info(f"Win Rate: {metrics['win_rate']:.2f}%")
        logger.info(f"Total ROI: {metrics['total_roi']:.2f}%")
        logger.info(f"Volume: ${metrics['total_volume']:.2f}")
        logger.info(f"Total Trades: {metrics['total_trades']}")
        logger.info(f"Total Token traded: {metrics['total_token_traded']}")

        toDatabase(logger, connection, cursor, address, metrics['gross_profit'], metrics['win_rate'], metrics['total_roi'], metrics['total_volume'], metrics['total_trades'], metrics['total_token_traded'])
        logger.info("--------------------------------------------------------------------------------------")
    else:
        logger.warning(f"File not found for address: {address}")

def main():
    logger.info("Starting continuous PnL calculation process")
    os.makedirs(INPUT_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    logger.info(f"Using start date: {START_DATE}")

    connection, cursor = connection_to_db(logger)

    while True:
        if os.path.exists(WALLET_ADDRESSES_FILE):
            addresses = read_addresses(WALLET_ADDRESSES_FILE)

            if addresses:
                # Traiter la première adresse (ou la dernière selon l'ordre désiré)
                address_to_process = addresses.pop(0)  # FIFO (premier entré, premier sorti)
                process_address(address_to_process, logger, connection, cursor)

                # Mettre à jour le fichier avec les adresses restantes
                write_addresses(WALLET_ADDRESSES_FILE, addresses)
            else:
                logger.info("No addresses to process. Waiting for new addresses...")
                time.sleep(5)  # Attendre avant de vérifier à nouveau
        else:
            logger.warning(f"Addresses file {WALLET_ADDRESSES_FILE} not found. Waiting for file creation...")
            time.sleep(5)

    #clear_input_folder(INPUT_FOLDER)
    close_sql_connection(logger, connection, cursor)
    logger.info("PnL calculation process completed")

if __name__ == "__main__":
    logger = setup_logger()
    main()
