import requests
import json
import sys
import os
import pandas as pd
from gradio_client import Client
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class BFCLCrawler(BaseCrawler):
    
    URL = "https://gorilla.cs.berkeley.edu/data.csv"
    
    MODEL_NAME_MAP = {
        'GPT-4-0125-Preview (Prompt)': 'GPT-4 Turbo 0125',
        'Claude-3-Opus-20240229 (Prompt)': 'Claude 3 Opus',
        'Gemini-1.5-Pro-Preview-0514 (FC)': 'Gemini 1.5 Pro 2024-05',
        'GPT-4-1106-Preview (FC)': 'GPT-4 Turbo',
        'GPT-4-turbo-2024-04-09 (Prompt)': 'GPT-4 Turbo 2024-04-09',
        'Gemini-1.5-Pro-Preview-0409 (FC)': 'Gemini 1.5 Pro',
        'Meta-Llama-3-70B-Instruct (Prompt)': 'Llama 3 70B',
        'GPT-4o-2024-05-13 (FC)': 'GPT-4o',
        'Claude-3-Sonnet-20240229 (Prompt)': 'Claude 3 Sonnet',
        'Mistral-Medium-2312 (Prompt)': 'Mistral Medium',
        'Gemini-1.5-Flash-Preview-0514 (FC)': 'Gemini 1.5 Flash',
        'Claude-3-Haiku-20240307 (Prompt)': 'Claude 3 Haiku',
        'Claude-2.1 (Prompt)': 'Claude 2.1',
        'Mistral-large-2402 (FC Auto)': 'Mistral Large',
        'Gemini-1.0-Pro-001 (FC)': 'Gemini 1.0 Pro',
        'GPT-3.5-Turbo-0125 (FC)': 'GPT-3.5 Turbo 16K 0125',
        'Meta-Llama-3-8B-Instruct (Prompt)': 'Llama 3 8B',
        'GPT-4-0613 (FC)': 'GPT-4 0613',
        'Gemma-7b-it (Prompt)': 'Gemma',
        'Claude-3.5-Sonnet-20240620 (Prompt)': 'Claude 3.5 Sonnet',
        '': '',
    }
    
    def __init__(self):
        super().__init__(
            topic='BFCL benchmark',
            desc="""
                The Berkeley Function Calling Leaderboard (also called Berkeley Tool Calling Leaderboard) evaluates the LLM's ability to call functions (aka tools) accurately.
                Which also includes the avg cost and latency data.
                Cost is calculated as an estimate of the cost per 1000 function calls, in USD. Latency is measured in seconds. For Open-Source Models, the cost and latency are calculated when serving with vLLM using 8 V100 GPUs. 
            """,
            tags=['LLM', 'machine learning', 'benchmark'],
            source_desc="""
                Official website: https://gorilla.cs.berkeley.edu/leaderboard.html
            """
        )
        
    def crawl(self):
        df = pd.read_csv(self.URL)
        
        # Keep only the 'Model' and 'Arena Elo' columns, and rename them
        df = df[['Model', 'Overall Acc', 'Cost ($ Per 1k Function Calls)', 'Latency Mean (s)']].rename(
            columns={'Model': 'name', 'Overall Acc': 'BFCL',
                     'Cost ($ Per 1k Function Calls)': 'function call cost ($/K calls)', 
                     'Latency Mean (s)': 'function call avg latency (s)'}
        )
        df['BFCL'] = df['BFCL'].str.replace('%', '').astype(float)

        print('Caution: these model names are not parsed, and will be disgarded.')
        print(df[~df['name'].isin(self.MODEL_NAME_MAP.keys())]['name'].unique())
        df = df[df['name'].isin(self.MODEL_NAME_MAP.keys())]
        df['name'] = df['name'].map(self.MODEL_NAME_MAP)
        df.set_index('name', inplace=True)
        print(df)
        self.raw_data = df
        
    def process(self):
        self.processed_data = pd.DataFrame(self.raw_data)
        
if __name__ == "__main__":
    crawler = BFCLCrawler()
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
    