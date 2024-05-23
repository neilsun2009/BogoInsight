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

class LMSYSArenaEloCrawler(BaseCrawler):
    
    URL = "https://lmsys-chatbot-arena-leaderboard.hf.space/"
    
    MODEL_NAME_MAP = {
        'GPT-4o-2024-05-13': 'GPT-4o',
        'GPT-4-Turbo-2024-04-09': 'GPT-4 Turbo 2024-04-09',
        'Gemini 1.5 Pro API-0409-Preview': 'Gemini 1.5 Pro',
        'GPT-4-1106-preview': 'GPT-4 Turbo',
        'Claude 3 Opus': 'Claude 3 Opus',
        'GPT-4-0125-preview': 'GPT-4 Turbo 0125',
        'Bard (Gemini Pro)': 'Gemini 1.0 Pro',
        'Llama-3-70b-Instruct': 'Llama 3 70B',
        'Claude 3 Sonnet': 'Claude 3 Sonnet',
        'GPT-4-0314': 'GPT-4',
        'Qwen-Max-0428': 'Qwen2.5 Max 0428',
        'Claude 3 Haiku': 'Claude 3 Haiku',
        'Qwen1.5-110B-Chat': 'Qwen1.5 110B',
        'GPT-4-0613': 'GPT-4 0613',
        'Llama-3-8b-Instruct': 'Llama 3 8B',
        'Mistral-Large-2402': 'Mistral Large',
        'Qwen1.5-72B-Chat': 'Qwen1.5 72B',
        'Claude-2.0': 'Claude 2',
        'GPT-3.5-Turbo-0613': 'GPT-3.5 Turbo 16K 0613',
        'Qwen1.5-14B-Chat': 'Qwen1.5 14B',
        'Claude-2.1': 'Claude 2.1',
        'GPT-3.5-Turbo-0314': 'GPT-3.5 Turbo 0301',
        'Mixtral-8x7b-Instruct-v0.1': 'Mixtral 8x7B',
        'GPT-3.5-Turbo-0125': 'GPT-3.5 Turbo 16K 0125',
        'Llama-2-70b-chat': 'Llama 2 70B',
        'Gemma-1.1-7B-it': 'Gemma',
        'Qwen1.5-7B-Chat': 'Qwen1.5 7B',
        'Claude-1': 'Claude',
        'Mistral Medium': 'Mistral Medium',
        'Mistral-7B-Instruct-v0.2': 'Mistral 7B',
        'GPT-3.5-Turbo-1106': 'GPT-3.5 Turbo 16K 1106',
        'Llama-2-13b-chat': 'Llama 2 13B',
        'Qwen-14B-Chat': 'Qwen 14B',
        'Llama-2-7b-chat': 'Llama 2 7B',
        'LLaMA-13B': 'LLaMA',
        'Qwen1.5-32B-Chat': 'Qwen1.5 32B',
        'Yi-Large-preview': 'Yi Large',
        'GLM-4-0116': 'GLM-4',
    }
    
    def __init__(self):
        super().__init__(
            topic='LMSYS Arena Elo',
            desc="""
                The LMSYS Arena is a platform for chatbot developers to test their chatbots against each other.
                The Elo rating system is used to rank the chatbots.
                This crawler fetches the leaderboard data.
            """,
            tags=['LLM', 'machine learning', 'benchmark'],
            source_desc="""
                Official blog: https://lmsys.org/blog/2023-05-03-arena/
                Online leaderboard: https://lmsys-chatbot-arena-leaderboard.hf.space/
                Paper: https://arxiv.org/abs/2403.04132
            """
        )
        
    def crawl(self):
        client = Client("lmsys/chatbot-arena-leaderboard")
        result = client.predict(
            category="Overall",
            api_name="/update_leaderboard_and_plots"
        )
        result = result[0]['value']
        df = pd.DataFrame(result['data'], columns=result['headers'])
        
        # Keep only the 'Model' and 'Arena Elo' columns, and rename them
        df = df[['Model', 'Arena Elo']].rename(columns={'Model': 'name', 'Arena Elo': 'LMSYS Arena Elo'})

        # Use regular expression to extract 'real_name' from the 'name' column
        df['name'] = df['name'].apply(lambda x: BeautifulSoup(x, 'html.parser').get_text())
        
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
    crawler = LMSYSArenaEloCrawler()
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
    