import requests
import json
import sys
import os
from io import BytesIO
import pandas as pd
import numpy as np
import shutil
from bs4 import BeautifulSoup
import unicodedata
print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.crawlers.llm_benchmark_crawlers import (
    LMSYSArenaEloCrawler, OpenCompassCrawler, BFCLCrawler
)
from BogoInsight.utils.logger import logger

class LLMSpecsCrawler(BaseCrawler):
    
    URL = "https://en.wikipedia.org/wiki/Large_language_model"
    
    ADDITIONAL_DATA_XLSX = "llm_additional_data.xlsx"
    
    COLUMN_NAME_MAP = {
        'Name': 'name',
        'Release date': 'period',
        'Developer': 'developer',
        'Number of parameters (billion)': 'parameters (B)',
        'Corpus size': 'corpus size (B tokens)',
        'Training cost (petaFLOP-day)': 'training cost (PFLOPS-day)',
        'License': 'license',
        # '': '',
        # '': '',
    }
    
    SELECTED_MODELS = [
        'GPT-1', 'GPT-2', 'GPT-3', 'GPT-4',
        'BERT', 'T5', 'Chinchilla', 'PaLM (Pathways Language Model)', 'PaLM 2 (Pathways Language Model 2)',
        'Ernie 3.0 Titan',
        'Claude', 'Claude 2', 'Claude 2.1', 'Claude 3', 
        'LLaMA (Large Language Model Meta AI)', 'Llama 2',
        'PanGu-Σ',
        'Mistral 7B', 'Mixtral 8x7B',
        'Grok-1',
        'Gemma',
    ]
    
    LICENSE_OS_MAP = {
        'Proprietary': 'close source',
        'Apache 2.0': 'open source',
        'Llama 2 license': 'open source',
        'Llama 3 license': 'open source',
        'tongyi-qianwen': 'open source',
        'MIT': 'open source',
        'Non-commercial research': 'open source',
        'beta': 'close source',
    }
    

    def __init__(self):
        super().__init__(
            topic='LLM Specs',
            desc="""
                Specs on leading large language models.
            """,
            tags=['LLM', 'machine learning'],
            source_desc="""
                Most information from Wikipedia: https://en.wikipedia.org/wiki/Large_language_model
                With most price data from OpenRouter: https://openrouter.ai/
                Most benchmark data from OpenCompass: https://rank.opencompass.org.cn/
                except for LMSYS Arena Elo score from LMSYS Arena: https://lmsys-chatbot-arena-leaderboard.hf.space/
                and BFCL score from BFCL: https://gorilla.cs.berkeley.edu/leaderboard.html
                Plus miscellaneous information manually gathered from various sources.
            """
        )


    def crawl(self):
        r = requests.get(self.URL, timeout=20)
        if r.status_code != 200:
            self._handle_crawl_failure(r)
        soup = BeautifulSoup(r.text, 'html.parser')
        # Remove all reference link anchors
        for sup in soup.find_all('sup'):
            sup.extract()
            
        # Find the section by title
        section = soup.find('span', {'class': 'mw-headline', 'id': 'List'}).parent
        
        # Find the first table in the section
        table_html = section.find_next_sibling('table')

        # Convert the HTML table to a pandas DataFrame
        table = pd.read_html(str(table_html))[0]
        
        # Replace all \xa0 characters with a space
        table = table.replace('\xa0', ' ', regex=True)
        table = table.replace('\xad', '', regex=True)
        table = table.replace('–', '')
        table = table.replace('‒', '')
        # Replace all 'Unknown' values with NaN
        table = table.replace('Unknown', pd.NA)
        
        self.raw_data = table
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
       
        
    def process(self):
        assert isinstance(self.raw_data, pd.DataFrame), "Raw data is not of type pd.DataFrame."

        df = pd.DataFrame(self.raw_data)
        
        print(df.columns)
        
        print(list(df['Name']))
        # Strip leading and trailing spaces from 'Name' column
        df['Name'] = df['Name'].str.strip()
        # Keep only the rows where the model column is in SELECTED_MODELS
        df = df[df['Name'].isin(self.SELECTED_MODELS)]
        
        # rename columns
        df.rename(columns=self.COLUMN_NAME_MAP, inplace=True)
        df = df.filter(items=self.COLUMN_NAME_MAP.values())
        
        # Remove ' (xxx)' part from 'name' column
        df['name'] = df['name'].str.replace(r' \(.*\)', '', regex=True)
        
        # Convert the 'period' column to datetime
        df['period'] = pd.to_datetime(df['period'])
        
        # Split models with multiple versions
        # Claude 3
        row = df.loc[df['name'] == 'Claude 3']
        for new_name in ['Claude 3 Opus', 'Claude 3 Sonnet', 'Claude 3 Haiku']:
            new_row = row.copy()
            new_row['name'] = new_name
            df = pd.concat([df, new_row], ignore_index=True)
        df = df.drop(df[df['name'] == 'Claude 3'].index)
        # Llama 2
        row = df.loc[df['name'] == 'Llama 2']
        for new_name in ['Llama 2 7B', 'Llama 2 13B', 'Llama 2 70B']:
            new_row = row.copy()
            new_row['name'] = new_name
            df = pd.concat([df, new_row], ignore_index=True)
        df = df.drop(df[df['name'] == 'Llama 2'].index)

        df = df.set_index('name')
        
        # Add additional information
        # Convert additional data to a DataFrame
        aux_df = pd.read_excel(self.ADDITIONAL_DATA_XLSX)
        aux_df = aux_df.set_index('name')
        # Update existing rows and columns
        df = aux_df.combine_first(df)
        # Append new rows
        # new_rows = aux_df.loc[~aux_df.index.isin(df.index)]
        # df = pd.concat([df, new_rows])
        # Add new columns
        for column in set(aux_df.columns) - set(df.columns):
            df[column] = aux_df[column]
        
        # add open source status
        df['license'] = df['license'].replace('proprietary', 'Proprietary')
        df['source access'] = df['license'].map(self.LICENSE_OS_MAP)
        
        # Replace 'Deepmind' and 'Google Deepmind' with 'Google' in 'developer' column
        df['developer'] = df['developer'].replace(['DeepMind', 'Google DeepMind'], 'Google')
        df['developer'] = df['developer'].replace(['Meta AI'], 'Meta')

        # Set the name of the index column to 'name'
        df.index.name = 'name'
        
        # append benchmark data
        crawlers = [
            OpenCompassCrawler(),
            LMSYSArenaEloCrawler(),
            BFCLCrawler(),
        ]
        for crawler in crawlers:
            print(f'\nMerging benchmark from {crawler.topic}...')
            crawler.crawl()
            crawler.process()
            df = df.combine_first(crawler.processed_data)
        
        # Reorder the columns
        top_columns = ['period', 'developer', 'parameters (B)', 
                       'input context window (K tkns)', 'max output tokens (K tkns)',
                       'input token price ($/M tkns)', 'output token price ($/M tkns)', 'input image price ($/K imgs)',
                       'source access']
        new_order = top_columns + [c for c in df.columns if c not in top_columns]
        df = df.reindex(new_order, axis=1)
        
        df.sort_values(by=['period', 'parameters (B)'], ascending=[False, False], inplace=True)
        self.processed_data = df
        
    
if __name__ == "__main__":
    crawler = LLMSpecsCrawler()
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