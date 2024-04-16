import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKForeignInvestmentCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "315-38011",
        "lang": "en",
        "cv": {
        "COUNTRY": [
            "VG",
            "CN",
            "GB",
            "KY",
            "BM",
            "US"
            ]
        },
        "sv": {
            "DI_POS_IDI": [
                "Raw_B_1dp_hkd_d"
            ],
            "DI_INCOME_OUTFLOW": [
                "Raw_B_1dp_hkd_d"
            ],
            "DI_INFLOW": [
                "Raw_B_1dp_hkd_d"
            ]
        },
        "period": {
            "start": "196101"
        },
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'DI_POS_IDI': 'year end direct investment position',
        'DI_INCOME_OUTFLOW': 'direct investment income outflow',
        'DI_INFLOW': 'direct investment inflow',
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        'HK$ billion': 'HK$B',
    }

    
    def __init__(self):
        super().__init__(
            topic='Hong Kong Foreign Investment',
            desc="""
                Foreign direct investment data of Hong Kong. 
                Yearly data since 1998.
                Including year-end position, direct inflow, and direct outflow.
            """,
            tags=['Hong Kong', 'foreign investment'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 315-38011
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=315-38011
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
        
        print(df['sv'].unique())
        print(df['svDesc'].unique())

        # Convert 'period' to datetime
        df['period'] = pd.to_datetime(df['period'], format='%Y')
        
        # Replace 'sv' values with their descriptions
        df['sv'] = df['sv'].map(self.SV_MAP)
        df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)
        df['COUNTRY'] = df['COUNTRY'].replace('', 'all')
        
        # Create a new column for 'sv'
        df['data_type'] = df['sv'] + ' ' + df['COUNTRY'] + ' (' + df['svDesc'] + ')'

        print(df.head())
        # print(df[df['sv'].isnull()])
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKForeignInvestmentCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')