import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKPopulationGrowthCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "110-01003",
        "lang": "en",
        "cv": {
            "TYPE_INFLOW": [
                "one-way",
                "others"
            ]
        },
        "sv": {
            "BIRTHS_PRO": [
                "Raw_K_1dp_per_n"
            ],
            "DEATHS_PRO": [
                "Raw_K_1dp_per_n"
            ],
            "PG": [
                "Raw_K_1dp_per_n"
            ],
            "PGR": [
                "Raw_1dp_%_n"
            ],
            "NI": [
                "Raw_K_1dp_per_n"
            ],
            "NM": [
                "Raw_K_1dp_per_n"
            ]
        },
        "period": {
            "start": "196101"
        },
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'BIRTHS_PRO': 'births',
        'DEATHS_PRO': 'deaths',
        'PG': 'population growth',
        'PGR': 'population growth rate',
        'NI': 'natural change',
        'NM': 'net movement'
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        '(\'000)': '\'000',
        '(%)': '%',
    }
    
    # a dictionary to map 'TYPE_INFLOW' values to their descriptions
    TYPE_INFLOW_MAP = {
        'one-way': 'one-way',
        'others': 'others',
        '': 'total'
    }
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong Population Growth',
            desc="""
                Population growth data of Hong Kong. 
                Including natural, immigration, and overall growth per half year.
            """,
            tags=['Hong Kong', 'population'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 110-01003
                
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
        
        print(df['svDesc'].unique())

        # Convert 'period' to datetime
        df['period'] = pd.to_datetime(df['period'], format='%Y%m')
        
        # Replace 'sv' values with their descriptions
        df['sv'] = df['sv'].map(self.SV_MAP)
        df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)

        # Replace 'TYPE_INFLOW' values with their descriptions
        df['TYPE_INFLOW'] = df['TYPE_INFLOW'].map(self.TYPE_INFLOW_MAP)

        # Create a new column for 'sv' and 'TYPE_INFLOW'
        df['data_type'] = df['sv']
        df.loc[df['sv'] == 'net movement', 'data_type'] += ' ' + df['TYPE_INFLOW'] + ' (' + df['svDesc'] + ')'
        df.loc[df['sv'] != 'net movement', 'data_type'] += ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKPopulationGrowthCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')