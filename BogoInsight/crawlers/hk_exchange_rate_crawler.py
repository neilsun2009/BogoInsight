import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKExchangeRateCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "340-46001",
        "lang": "en",
        "cv": {},
        "sv": {
            "FC_JPY": [
                "Raw_4dp_hkd_d"
            ],
            "FC_GBP": [
                "Raw_2dp_hkd_d"
            ],
            "FC_USD": [
                "Raw_3dp_hkd_d"
            ],
            "FC_CNY": [
                "Raw_4dp_hkd_d"
            ],
            "FC_EUR": [
                "Raw_2dp_hkd_d"
            ]
        },
        "period": {
            "start": "197501"
        },
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'FC_JPY': 'exchange rate JPY to HKD',
        'FC_CNY': 'exchange rate CNY to HKD',
        'FC_USD': 'exchange rate USD to HKD',
        'FC_GBP': 'exchange rate GBP to HKD',
        'FC_EUR': 'exchange rate EUR to HKD',
    }

    
    def __init__(self):
        super().__init__(
            topic='Hong Kong Exchange Rate',
            desc="""
                Exchange rate data of Hong Kong, monthly, since 1975.
                Selected data of RMB, USD, GBP, EUR and JPY to HKD.
            """,
            tags=['Hong Kong', 'exchange rate'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 340-46001
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=340-46001
            """
        )

    def crawl(self):
        data = {'query': json.dumps(self.PARAMETERS)}
        r = requests.post(self.URL, data=data, timeout=20)
        if r.status_code != 200:
            self._handle_crawl_failure(r)
        self.raw_data = r.json()['dataSet']
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
        
    def process(self):
        assert type(self.raw_data) == list, "Raw data is not in the correct format."

        # Assuming self.raw_data is your list of dictionaries
        df = pd.DataFrame(self.raw_data)
        
        print(df.head(10))
        
        print(df['svDesc'].unique())
        
        # remove data with 'freq' == 'Y'
        df = df[df['freq'] != 'Y']

        # Convert 'period' to datetime
        df['period'] = pd.to_datetime(df['period'], format='%Y%m')
        
        # Replace 'sv' values with their descriptions
        df['data_type'] = df['sv'].map(self.SV_MAP)
        # df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)
        
        # Create a new column for 'sv' and 'TYPE_INFLOW'
        # df['data_type'] = df['sv'] + ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKExchangeRateCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')