from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import time
from wallet_api.spiders.defi_parser import DefiParserSpider

with open('config.json', 'r') as f:
    config = json.load(f)

def run_scraper(wallet_addresses):
    try:
        output_directory = config["walletProcess_dir"]
        
        # Récupérer les paramètres du projet Scrapy
        settings = get_project_settings()
        settings.set('TELNETCONSOLE_ENABLED', False)  # Désactiver le Telnet console
        settings.set('LOG_LEVEL', 'WARN')  # Afficher uniquement les messages de niveau WARNING et supérieur

        process = CrawlerProcess(settings=settings)
        for Wallet_addy in wallet_addresses:
            custom_url = f"https://api-v2.solscan.io/v2/account/activity/dextrading?address={Wallet_addy}&page={{page}}&page_size=100"
            output_filename = f"{Wallet_addy}.csv"

            process.crawl(DefiParserSpider,
                          address=Wallet_addy,
                          output_dir=output_directory,
                          filename=output_filename,
                          custom_url=custom_url)
        
        start_time = time.time()  # Enregistrer le temps de début
        process.start()
        end_time = time.time()  # Enregistrer le temps de fin

        total_time = end_time - start_time
        print(f"Le scraping a pris {total_time:.2f} secondes pour s'exécuter.")
    except Exception as e:
        print(f"Erreur lors du crawling: {e}")

if __name__ == "__main__":
    wallet_addresses = [
        "HzkLu4hBwtn6xdiFZ4GgtFzLQdhwtBT1nAEUxDHTpemd",
        "rAkF7sr35MasvQ48ss4uCEn8ijHdDaxBrNpTqaGNGoF",
        "A5TYS17zBnd8TUEr2GyHzysBqisBUnG8seRZrMxaK4Ku",
        "2L2AiV9T1pxfF67jPrFpVYnnTnCWm2QXejTTsCLtoH5C",
#        "4DdrfiDHpmx55i4SPssxVzS9ZaKLb8qr45NKY9Er9nNh",
        "Haee7H5bKDCnm6dXLkeR9DcWw9Puhnkwk71QBUSHcpUt",
        "C8SVWzmSvoYKfQKjkmr7Vz4hk13MGBxWXcynhEYEpddi"
    ]
    run_scraper(wallet_addresses)