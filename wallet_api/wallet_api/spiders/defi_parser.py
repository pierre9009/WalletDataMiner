import scrapy
from scrapy.selector import Selector
import re
import os
import pandas as pd
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
        "Origin": "https://solscan.io",
        "Alt-Used": "api-v2.solscan.io",
        "Connection": "keep-alive",
        "Referer": "https://solscan.io/",
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
        self.path = os.path.join(output_dir , filename)

    def start_requests(self):
        yield scrapy.Request(url=self.url,callback=self.parse, headers=self.headers)


    def parse(self, response):
        raw_data = response.body
        data = json.loads(raw_data)

        df = pd.DataFrame([{
            "block_id": tx["block_id"],
            "trans_id": tx["trans_id"],
            "block_time": tx["block_time"],
            "token1": tx["amount_info"]["token1"],
            "token2": tx["amount_info"]["token2"],
            "decimal1": tx["amount_info"]["token1_decimals"],
            "decimal2": tx["amount_info"]["token2_decimals"],
            "amount1": tx["amount_info"]["amount1"],
            "amount2": tx["amount_info"]["amount2"]
        } for tx in data['data']])
        df.to_csv(path_or_buf = self.path)