import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKGDPCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "310-31001",
        "lang": "en",
        "cv": {
        },
        "sv": {
            "CUR": [
                "Raw_M_hkd_d",
                "YoY_1dp_%_s"
            ],
            "CON": [
                "Raw_M_hkd_d",
                "YoY_1dp_%_s"
            ],
            "DEF": [
                "Raw_1dp_idx_n",
                "YoY_1dp_%_s"
            ],
            "SA1": [
                "QoQ_1dp_%_s"
            ],
        },
        "period": {
            "start": "199003",
        },
        "freq": "Q",
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'CUR': 'GDP current',
        'CON': 'GDP chained (2021)',
        'DEF': 'implicit price deflator',
        'SA1': 'GDP seasonally adjusted',
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        'HK$ million': 'M HKD',
        'Year-on-year % change': 'rate YoY',
        'Index (Year 2021=100)': 'index 2021=100',
        'Quarter-to-quarter % change': 'rate QoQ',
    }
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong GDP Growth',
            desc="""
                GDP data of Hong Kong. 
                Including GDP in current and chained dollars, as well as change rates (by year & seasonly changed by quarter).
                Also including implicit price deflator.
            """,
            tags=['Hong Kong', 'population'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 310-31001
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=110-01003
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
        df['sv'] = df['sv'].map(self.SV_MAP)
        df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)
        
        # Create a new column for 'sv' and 'TYPE_INFLOW'
        df['data_type'] = df['sv'] + ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKGDPCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')