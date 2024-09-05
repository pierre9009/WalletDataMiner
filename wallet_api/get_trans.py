#get_trans.py
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from wallet_api.spiders.defi_parser import DefiParserSpider

from config import WALLET_TOPROCESS, SOLSCAN_API_URL
import time


def run_scraper(wallet_addresses,logger):
    try:        
        # Récupérer les paramètres du projet Scrapy
        settings = get_project_settings()
        settings.set('TELNETCONSOLE_ENABLED', False)  # Désactiver le Telnet console
        settings.set('LOG_LEVEL', 'CRITICAL')  # Définir le niveau de log à INFO
        process = CrawlerProcess(settings=settings)

        for Wallet_addy in wallet_addresses:
            url = SOLSCAN_API_URL.format(address=Wallet_addy)
            output_filename = f"{Wallet_addy}.csv"

            process.crawl(DefiParserSpider,
                          address=Wallet_addy,
                          output_dir=WALLET_TOPROCESS,
                          filename=output_filename,
                          custom_url=url)
        
        start_time = time.time()  # Enregistrer le temps de début
        process.start()
        end_time = time.time()  # Enregistrer le temps de fin

        total_time = end_time - start_time
        logger.info(f"Le scraping a pris {total_time:.2f} secondes pour s'exécuter.")
    except Exception as e:
        logger.info(f"Erreur lors du crawling: {e}")
