import requests
import json
import sys
import os
from io import BytesIO
import pandas as pd
import numpy as np
import shutil
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKHouseRentalIndexCrawler(BaseCrawler):
    
    URL = "https://www.rvd.gov.hk/doc/en/statistics/his_data_3.xls"
    
    COLUMN_NAMES = [
        'year', 
        'month', 
        'house rental A, < 40m^2 (idx 1999=100)', 
        'house rental B, 40~69 m^2 (idx 1999=100)', 
        'house rental C, 70~99 m^2 (idx 1999=100)', 
        'house rental D, 100~159 m^2 (idx 1999=100)', 
        'house rental E, >= 160 m^2 (idx 1999=100)', 
        'house rental ABC, < 100 m^2 (idx 1999=100)',
        'house rental DE, >= 100 m^2 (idx 1999=100)',
        'house rental all (idx 1999=100)',
    ]
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong House Rental Index',
            desc="""
                House rental index of Hong Kong by month from 1993 by class.
            """,
            tags=['Hong Kong', 'house rental'],
            source_desc="""
                Rating and Valuation Department, HKSAR
                
                URL: https://www.rvd.gov.hk/en/publications/property_market_statistics.html
            """
        )


    def crawl(self):
        r = requests.get(self.URL, timeout=20)
        if r.status_code != 200:
            self._handle_crawl_failure(r)
        data = pd.read_excel(BytesIO(r.content), 
                             sheet_name='Monthly  按月', 
                             header=None,
                             names=self.COLUMN_NAMES, 
                             usecols='B,F,I,L,O,R,U,X,AA,AD', 
                             dtype={'month': int},
                             skiprows=7,
                             skipfooter=6)
        data['year'].replace(' ', np.nan, inplace=True)
        data['year'].fillna(method='ffill', inplace=True)
        data['year'] = data['year'].astype(int)  # Convert 'year' to integer after filling NaNs
        data['month'] = data['month'].apply(lambda x: f'{x:02d}')
        data['period'] = pd.to_datetime(data[['year', 'month']].astype(str).agg('-'.join, axis=1))
        data.set_index('period', inplace=True)
        data.drop(columns=['year', 'month'], inplace=True)
        self.raw_data = data
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
       
        
    def process(self):
        assert isinstance(self.raw_data, pd.DataFrame), "Raw data is not of type pd.DataFrame."

        df = pd.DataFrame(self.raw_data)
        growth_rate_column_name = 'house rental growth all (% rate MoM)'
        df[growth_rate_column_name] = df['house rental all (idx 1999=100)'].pct_change() * 100
        df[growth_rate_column_name] = df[growth_rate_column_name].round(2)
        self.processed_data = df
        
if __name__ == "__main__":
    crawler = HKHouseRentalIndexCrawler()
    crawler.crawl()
    print(crawler.raw_data.head())
    crawler.process()
    print(crawler.processed_data.head())
    # delete previously output files
    output_base = f"../data/{crawler.topic.replace(' ', '_').lower()}"
    if os.path.exists(output_base):
        shutil.rmtree(output_base)
    # output
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')