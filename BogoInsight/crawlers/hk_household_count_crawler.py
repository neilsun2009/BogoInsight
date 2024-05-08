import requests
import json
import sys
import os
import pandas as pd
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class HKHouseholdCountCrawler(BaseCrawler):
    
    URL = "https://www.censtatd.gov.hk/api/post.php"
    
    PARAMETERS ={
        "id": "130-06604",
        "lang": "en",
        "cv": {
            "TENURE": [
                "1",
                "2",
                "3",
                "4",
                "5",
                "1.1",
                "1.2"
            ]
        },
        "sv": {
            "DH": [
                "Raw_K_1dp_hh_n",
                "Prop_1dp_%_n"
            ]
        },
        "period": {
            "start": "200201"
        },
        "freq": "Q",
    }
    
    # a dictionary to map 'sv' values to their descriptions
    SV_MAP = {
        'DH': 'households',
    }
    
    # a dictionary to map 'svDesc' values to their descriptions
    SV_DESC_MAP = {
        'Percentage share (%)': '%',
        "No. ('000)": "'000",
    }
    
    # a dictionary to map 'TENUREDesc' values to their descriptions
    TENURE_DESC_MAP = {
        'Total': 'total',
        "Owner-occupiers": "owner-occupier total",
        "Residing in private sector housing": "private owner-occupiers",
        "Residing in public sector housing": "public owner-occupiers",
        "Sole tenants": "sole tenants",
        "Co-tenants": "co-tenants",
        "Accommodation provided by employers": "accommodation provided by employers",
        "Others": "others",
    }
    
    
    def __init__(self):
        super().__init__(
            topic='Hong Kong Household Count',
            desc="""
                Household count data of Hong Kong.
                Including the number of households by types, as well as their percentages.
            """,
            tags=['Hong Kong', 'household'],
            source_desc="""
                Census and Statistics Department, HKSAR
                
                ID: 130-06604
                
                URL: https://www.censtatd.gov.hk/en/web_table.html?id=130-06604
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
        
        # only keep quarter data
        df['month'] = df['period'].dt.month
        df = df[df['month'].isin([3, 6, 9, 12])]
        df = df.drop(columns=['month'])

        # Replace 'sv' values with their descriptions
        df['sv'] = df['sv'].map(self.SV_MAP)
        df['svDesc'] = df['svDesc'].map(self.SV_DESC_MAP)
        df['TENUREDesc'] = df['TENUREDesc'].map(self.TENURE_DESC_MAP)
        
        # Create a new column for 'sv' and 'TYPE_INFLOW'
        df['data_type'] = df['sv'] + ' ' + df['TENUREDesc'] + ' (' + df['svDesc'] + ')'

        print(df.head())
        print(df['data_type'].unique())
        print(df.isnull().sum())
        # Pivot the DataFrame to wide format
        df_pivot = df.pivot(index='period', columns='data_type', values='figure')

        # Calculate the percentage change for households
        df_pivot['household growth rate (%)'] = df_pivot["households total ('000)"].pct_change() * 100
        df_pivot['household growth rate (%)'] = df_pivot["household growth rate (%)"].round(2)

        # Now df_pivot is the transformed DataFrame in wide format
        self.processed_data = df_pivot
        
if __name__ == "__main__":
    crawler = HKHouseholdCountCrawler()
    crawler.crawl()
    crawler.process()
    print(crawler.processed_data.head())
    crawler.export_csv(f'../data/{crawler._gen_default_export_name()}')