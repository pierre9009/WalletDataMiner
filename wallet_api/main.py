from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import scrapy
from scrapy.crawler import CrawlerProcess
from solScraper.solScraper.spiders.solWallet import SolwalletSpider

def time_cut(start_timestamp, end_timestamp):
    one_week = 604800  # Durée d'une semaine en secondes
    intervals = []

    if (end_timestamp - start_timestamp) > one_week:
        current_start = start_timestamp
        while current_start + one_week < end_timestamp:
            current_end = current_start + one_week
            intervals.append((current_start, current_end))
            current_start = current_end + 1  # Commence le prochain intervalle une seconde après la fin du précédent
        intervals.append((current_start, end_timestamp))  # Ajouter le dernier intervalle
    else:
        intervals.append((start_timestamp, end_timestamp))
    
    return intervals

def run_scraper(wallet_addresses, timestamp):
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
        output_directory = config["walletProcess_dir"]
        
        # Récupérer les paramètres du projet Scrapy
        settings = get_project_settings()
        settings.set('TELNETCONSOLE_ENABLED', False)  # Désactiver le Telnet console

        process = CrawlerProcess(settings=settings)
        for i in range(len(timestamp)):
            for Wallet_addy in wallet_addresses:
                custom_url = f"https://api-v2.solscan.io/v2/account/transfer/export?address={Wallet_addy}&block_time[]={timestamp[i][0]}&block_time[]={timestamp[i][1]}&page=1"
                output_filename = f"{Wallet_addy}_{i}.csv"

                process.crawl(SolwalletSpider,
                              address=Wallet_addy,
                              url=custom_url,
                              output_dir=output_directory,
                              filename=output_filename)
        
        process.start()
    except Exception as e:
        print(f"Erreur lors du crawling: {e}")

if __name__ == "__main__":
    wallet_addresses = [
        "HzkLu4hBwtn6xdiFZ4GgtFzLQdhwtBT1nAEUxDHTpemd",
        "rAkF7sr35MasvQ48ss4uCEn8ijHdDaxBrNpTqaGNGoF",
        "A5TYS17zBnd8TUEr2GyHzysBqisBUnG8seRZrMxaK4Ku"
    ]
    start_timestamp = 1721150732 - 604800


    end_timestamp = 1721150732

    timestamp = time_cut(start_timestamp, end_timestamp)
    run_scraper(wallet_addresses, timestamp)