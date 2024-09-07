# main.py
from config import INPUT_FOLDER, OUTPUT_FOLDER, START_DATE
from adresses import WALLET_ADDRESSES

from logger import setup_logger
from price_utils import load_sol_price_cache, save_sol_price_cache, get_sol_price_at_time, get_token_prices
from pnl_calculation import process_transaction, calculate_unrealized_pnl, calculate_pnl_and_generate_summary
from file_utils import clear_input_folder
from get_trans import run_scraper

import os
from playsound import playsound

def main():
    
    logger.info("Starting download process")
    run_scraper(WALLET_ADDRESSES, logger)
    logger.info("Starting PnL calculation process")
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    logger.info(f"Using start date: {START_DATE}")
    address_pnls = {}

    for filename in os.listdir(INPUT_FOLDER):
        if filename.endswith('.csv'):
            file_path = os.path.join(INPUT_FOLDER, filename)
            address = filename.split('.')[0]
            logger.info(f"Processing file for address: {address}")

            metrics = calculate_pnl_and_generate_summary(logger, file_path, OUTPUT_FOLDER, START_DATE)
            address_pnls[address] = (metrics['total_realized_pnl'], metrics['total_unrealized_pnl'])
            
            # Afficher les métriques de trading
            logger.info(f"Trading metrics for {address}:")
            logger.info(f"Gross Profit: ${metrics['gross_profit']:.2f}")
            logger.info(f"Win Rate: {metrics['win_rate']:.2f}%")
            logger.info(f"Total ROI: {metrics['total_roi']:.2f}%")
            logger.info(f"Volume: ${metrics['total_volume']:.2f}")
            logger.info(f"Total Trades: {metrics['total_trades']}")
            logger.info(f"Total Token traded: {metrics['total_token_traded']}")
            
            logger.info("--------------------------------------------------------------------------------------")
    clear_input_folder(INPUT_FOLDER)
    logger.info("PnL calculation process completed")
    playsound('./finished.mp3')

if __name__ == "__main__":
    logger = setup_logger()
    main()