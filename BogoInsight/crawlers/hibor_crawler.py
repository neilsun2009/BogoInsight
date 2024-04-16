import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HiborCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "340-45022",
        "lang": "en",
        "cv": {
            "MATURITY": [
                "0N",
                "1W",
                "1M",
                "3M",
                "6M"
            ]
        },
        "sv": {
            "SET_RATE": [
                "Rate_2dp_%_n"
            ]
        },
        "period": {
            "start": "199607"
        },
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'SET_RATE': 'HIBOR',
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        'Rates at end of period(percent per annum)': '% p.a.',
    }
    
    def __init__(self):
        super().__init__(
            topic='HIBOR',
            desc="""
                Hong Kong Dollar Interest Settlement Rates, commonly known as HIBOR (Hong Kong Interbank Offered Rate).
                This is the basic component for type H mortage rate in HK, and can be seen as a more effective indicator of the interest rate then the best lending rate.
                Quarterly data since Q3 1996.
            """,
            tags=['Hong Kong', 'interest rate'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 340-45022
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=340-45022
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
        df['data_type'] = df['sv'] + ' ' + df['MATURITY'] + ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HiborCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')