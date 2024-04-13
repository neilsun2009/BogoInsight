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

class HKHouseVacancyCrawler(BaseCrawler):
    
    URL = "https://www.rvd.gov.hk/doc/en/statistics/private_domestic.xls"
    
    COLUMN_NAMES = [
        'year', 
        'house vacancy A, < 40m^2 (num)', 
        'house vacancy A, < 40m^2 (%)', 
        'house vacancy B, 40~69 m^2 (num)', 
        'house vacancy B, 40~69 m^2 (%)', 
        'house vacancy C, 70~99 m^2 (num)', 
        'house vacancy C, 70~99 m^2 (%)', 
        'house vacancy D, 100~159 m^2 (num)', 
        'house vacancy D, 100~159 m^2 (%)', 
        'house vacancy E, >= 160 m^2 (num)', 
        'house vacancy E, >= 160 m^2 (%)', 
        'house vacancy all (num)', 
        'house vacancy all (%)', 
    ]
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong House Vacancy',
            desc="""
                House vacancy of Hong Kong by year from 1982 by class.
                
                Note: village houses are excluded since 2004.
            """,
            tags=['Hong Kong', 'house vacancy'],
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
                             sheet_name='Vacancy_空置量', 
                             header=None,
                             names=self.COLUMN_NAMES, 
                             usecols='C,E:P', 
                             dtype={'year': int},
                             skiprows=15,
                             skipfooter=6)
        print(data.head(10))
        data['period'] = pd.to_datetime(data['year'], format='%Y')
        data.set_index('period', inplace=True)
        data.drop(columns=['year'], inplace=True)
        # restore percentage values
        for col in data.columns:
            if col.endswith('(%)'):
                data[col] = (data[col] * 100).round(2)
        
        self.raw_data = data
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
       
        
    def process(self):
        assert isinstance(self.raw_data, pd.DataFrame), "Raw data is not of type pd.DataFrame."

        df = pd.DataFrame(self.raw_data)
        growth_rate_column_name = 'house vacancy growth all (% rate YoY)'
        df[growth_rate_column_name] = df['house vacancy all (num)'].pct_change() * 100
        df[growth_rate_column_name] = df[growth_rate_column_name].round(2)
        self.processed_data = df
        
if __name__ == "__main__":
    crawler = HKHouseVacancyCrawler()
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