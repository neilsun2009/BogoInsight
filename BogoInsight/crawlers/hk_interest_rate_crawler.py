import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKInterestRateCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "340-45021",
        "lang": "en",
        "cv": {
            "DEP_P_T": [
                "1W",
                "1M",
                "3M",
                "6M",
                "12M"
            ]
        },
        "sv": {
            "BL_RATE": [
                "Rate_2dp_%_n"
            ],
            "S_DEP_RATE": [
                "Rate_2dp_%_n"
            ],
            "T_DEP_RATE": [
                "Rate_2dp_%_n"
            ]
        },
        "period": {
            "start": "196101"
        },
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'BL_RATE': 'best lending rate',
        'S_DEP_RATE': 'savings deposit rate',
        'T_DEP_RATE': 'time deposit rate',
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        '(Percent for annum)': '% p.a.',
    }
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong Interest Rate',
            desc="""
                Interest rate data of Hong Kong.
                Including time deposit rates, savings deposit rates and "best lending rates" (lending rates by HSBC).
            """,
            tags=['Hong Kong', 'population'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 340-45021
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=340-45021
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
        
        print(df['svDesc'].unique())
        
        # remove data with 'freq' == 'Y'
        df = df[df['freq'] != 'Y']

        # Convert 'period' to datetime
        df['period'] = pd.to_datetime(df['period'], format='%Y%m')
        
        # Replace 'sv' values with their descriptions
        df['sv'] = df['sv'].map(self.SV_MAP)
        df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)

        # Create a new column for 'sv' and 'DEP_P_T'
        df['data_type'] = df['sv']
        df.loc[df['sv'] == 'time deposit rate', 'data_type'] += ' ' + df['DEP_P_T'] + ' (' + df['svDesc'] + ')'
        df.loc[df['sv'] != 'time deposit rate', 'data_type'] += ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKInterestRateCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')