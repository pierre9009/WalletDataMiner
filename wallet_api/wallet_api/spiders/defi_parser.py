import scrapy
from scrapy.selector import Selector
import re
import os
import json

class DefiParserSpider(scrapy.Spider):
    name = "defi_parser"
    start_urls = ['https://solscan.io/']
    headers = {
        "Host": "api-v2.solscan.io",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "sol-aut": "4W-mJSB9dls0fKiy=ScEu=3J0=pRlOhJnWpQILY3",
        "Origin": "https://solscan.io",
        "Alt-Used": "api-v2.solscan.io",
        "Connection": "keep-alive",
        "Referer": "https://solscan.io/",
        "Cookie": "cf_clearance=AF60KY5NZcyFBRvS7D.uSbitCChuZEvOlOBnKzq7S1w-1721551929-1.0.1.1-skkjPUo5cLwHzw4.BtGELvOqhilWv5kilG9rzAyAblNtZLazkC8vJIUeMHBpi2LIOIbWXdrQINhHVW7hvnkIEQ",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "TE": "trailers"
    }
    url = "https://api-v2.solscan.io/v2/account/activity/dextrading?address=CuvaikSrjiwvsBs8W51oRomA3vgjQdgSVxFgXLyhnKq5&page=1&page_size=100"
    
    def __init__(self, address='', output_dir='', filename='output.csv', url=None, *args, **kwargs):
        super(DefiParserSpider, self).__init__(*args, **kwargs)
        self.address = address
        self.start_url = url
        self.output_dir = output_dir
        self.filename = filename


    def start_requests(self):
        
        # Vérifie si l'URL a été fournie

        # Première requête pour récupérer le chiffre
        yield scrapy.Request(url=self.url,callback=self.parse, headers=self.headers)


    def parse(self, response):
        raw_data = response.body
        data = json.loads(raw_data)
        for tx in data['data']:
            print("TX : ")
            print(tx['trans_id'])
            print()
        