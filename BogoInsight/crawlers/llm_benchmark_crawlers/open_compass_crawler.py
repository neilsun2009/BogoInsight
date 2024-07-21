import requests
import json
import sys
import os
import pandas as pd

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from BogoInsight.crawlers.base_crawler import BaseCrawler
from BogoInsight.utils.logger import logger

class OpenCompassCrawler(BaseCrawler):
    
    OPEN_COMPASS_RANKING_URL = "https://opencompass.oss-cn-shanghai.aliyuncs.com/assets/llm-rank/llm-data-v2.json"
    VISION_RANKING_URL = "https://opencompass.oss-cn-shanghai.aliyuncs.com/assets/mm-rank/mmlb-data.json"
    COMMUNITY_RANKING_URL = "https://opencompass.oss-cn-shanghai.aliyuncs.com/assets/large-language-dataset-data.json"
    
    MODEL_NAME_MAP = {
        # open compass
        'GPT-4o-20240513': 'GPT-4o',
        'GPT-4-Turbo-20240409': 'GPT-4 Turbo 2024-04-09',
        'GPT-4-Turbo-1106': 'GPT-4 Turbo',
        'Claude3-Opus': 'Claude 3 Opus',
        'Llama3-70B-Instruct': 'Llama 3 70B',
        'Qwen1.5-110B-Chat': 'Qwen1.5 110B',
        'Qwen-Max-0403': 'Qwen2 Max 0403',
        'ERNIE-4.0-8K-0329': 'Ernie 4.0',
        'Qwen1.5-72B-Chat': 'Qwen1.5 72B',
        'Moonshot-v1-8K': 'Moonshot V1 8K',
        'Mistral-Large': 'Mistral Large',
        'Qwen-72B-Chat': 'Qwen 72B',
        'Qwen1.5-14B-Chat': 'Qwen1.5 14B',
        'Qwen1.5-32B-Chat': 'Qwen1.5 32B',
        'GPT-3.5-Turbo': 'GPT-3.5 Turbo 16K 0613',
        'Qwen-14B-Chat': 'Qwen 14B',
        'Llama3-8B-Instruct': 'Llama 3 8B',
        'Qwen1.5-7B-Chat': 'Qwen1.5 7B',
        'Mixtral-8x7B-Instruct-v0.1': 'Mixtral 8x7B',
        'Qwen-7B-Chat': 'Qwen 7B',
        'LLaMA-2-70B-Chat': 'Llama 2 70B',
        'Mistral-7B-Instruct-v0.2': 'Mistral 7B',
        'LLaMA-2-13B-Chat': 'Llama 2 13B',
        'LLaMA-2-7B-Chat': 'Llama 2 7B',
        'GLM-4': 'GLM-4',
        'Qwen-Max-0428': 'Qwen2.5 Max 0428',
        'Yi-Large': 'Yi Large',
        # vision
        'GPT-4o, 20240513': 'GPT-4o',
        'GPT-4v, 20240409': 'GPT-4 Turbo 2024-04-09',
        'GPT-4v-20240409': 'GPT-4 Turbo 2024-04-09',
        'Qwen-VL-Max': 'Qwen VL Max',
        'GPT-4v, 20231106': 'GPT-4 Vision Preview',
        'Qwen-VL-Plus': 'Qwen VL Plus',
        # 'Claude-3V Sonnet': 'Claude 3 Sonnet',
        'Claude-3-Sonnet': 'Claude 3 Sonnet',
        'Claude-3V Opus': 'Claude 3 Opus',
        # 'Claude-3V Haiku': 'Claude 3 Haiku',
        'Claude-3-Haiku': 'Claude 3 Haiku',
        'PaliGemma-3B-mix-448': 'PaliGemma',
        'Qwen-VL-Chat': 'Qwen VL',
        'GeminiProVision': 'Gemini 1.0 Pro',
        'GLM-4v': 'GLM-4V',
        'Claude3.5-Sonnet': 'Claude 3.5 Sonnet',
        'Gemini-1.5-Pro': 'Gemini 1.5 Pro',
        'Gemini-1.0-Pro': 'Gemini 1.0 Pro',
        'GPT-4o-mini-20240718': 'GPT-4o-mini',
        'GPT-4v-20231106': 'GPT-4 Vision Preview',
        'Phi-3-Vision': 'Phi-3 Vision',
        'Qwen-VL': 'Qwen VL',
        # community
        'GPT-4': 'GPT-4',
        'Qwen-72B': 'Qwen 72B',
        'ChatGPT': 'GPT-3.5',
        'Qwen-14B': 'Qwen 14B',
        'Claude-1': 'Claude',
        'LLaMA-65B': 'LLaMA',
        'Qwen-7B': 'Qwen 7B',
        'LLaMA-2-13B': 'Llama 2 13B',
        'LLaMA-2-7B': 'Llama 2 7B',
        'LLaMA-2-70B': 'Llama 2 70B',
        'Qwen-1.8B': 'Qwen 1.8B',
        '': '',
    }
    
    def __init__(self):
        super().__init__(
            topic='OpenCompass benchmark',
            desc="""
                OpenCompass is a benchmark platform for LLMs.
                They host their own ranking system, as well as inportant community benchmarks.
                Another highlight is the dedicated leaderboard for Chinese language support.
            """,
            tags=['LLM', 'machine learning', 'benchmark'],
            source_desc="""
                OpenCompass: https://rank.opencompass.org.cn/
            """
        )
        
    def crawl(self):
        # open compass ranking
        response = requests.get(self.OPEN_COMPASS_RANKING_URL)
        data = response.json()
        df_open_compass = pd.DataFrame(data['OverallTable'])
        df_open_compass = df_open_compass[['model', 'Average', 'Average_CN', 'Average_EN']].rename(
            columns={'model': 'name', 'Average': 'OpenCompass avg',
                     'Average_CN': 'OpenCompass CN', 'Average_EN': 'OpenCompass EN'}
        )
        
        print('Caution: these model OpenCompass names are not parsed, and will be disgarded.')
        print(df_open_compass[~df_open_compass['name'].isin(self.MODEL_NAME_MAP.keys())]['name'].unique())
        df_open_compass = df_open_compass[df_open_compass['name'].isin(self.MODEL_NAME_MAP.keys())]
        df_open_compass['name'] = df_open_compass['name'].map(self.MODEL_NAME_MAP)
        df_open_compass.set_index('name', inplace=True)
        print(df_open_compass.head())
        
        # vision ranking
        response = requests.get(self.VISION_RANKING_URL)
        data = response.json()['Main']
        for item in data:
            item['name'] = item['Method'][0]
        df_vision = pd.DataFrame(data)
        df_vision = df_vision[['name', 'MMMU_VAL', 'MathVista']].rename(
            columns={'MMMU_VAL': 'MMMU',}
        )
        
        print('Caution: these VISION model names are not parsed, and will be disgarded.')
        print(df_vision[~df_vision['name'].isin(self.MODEL_NAME_MAP.keys())]['name'].unique())
        df_vision = df_vision[df_vision['name'].isin(self.MODEL_NAME_MAP.keys())]
        df_vision['name'] = df_vision['name'].map(self.MODEL_NAME_MAP)
        df_vision.set_index('name', inplace=True)
        print(df_vision.head())
        
        # community benchmark ranking
        response = requests.get(self.COMMUNITY_RANKING_URL)
        data = response.json()
        df_comm = pd.DataFrame()
        for key in ['MMLU', 'DROP', 'MATH', 'HumanEval', ]:
            values = data[key]['evalTableData']
            metric_keyname = key.lower()
            if key == 'HumanEval':
                metric_keyname = 'openaihumaneval'
            benchmark_data = [{'name': item['model'], key: item[metric_keyname]} for item in values]
            temp_df = pd.DataFrame(benchmark_data).set_index('name')
            df_comm = pd.concat([df_comm, temp_df], axis=1)
        
        print(df_comm)
        df_comm.reset_index(inplace=True)
        print('Caution: these COMMUNITY BENCHMARK model names are not parsed, and will be disgarded.')
        print(df_comm[~df_comm['name'].isin(self.MODEL_NAME_MAP.keys())]['name'].unique())
        df_comm = df_comm[df_comm['name'].isin(self.MODEL_NAME_MAP.keys())]
        df_comm['name'] = df_comm['name'].map(self.MODEL_NAME_MAP)
        df_comm.set_index('name', inplace=True)
        print(df_comm.head())
        
        self.raw_data = df_open_compass.merge(df_vision, how='outer', left_index=True, right_index=True)
        self.raw_data = self.raw_data.merge(df_comm, how='outer', left_index=True, right_index=True)
        # self.raw_data = self.raw_data.set_index('name')
        self.raw_data = self.raw_data.reset_index().drop_duplicates(subset='name').set_index('name')
        
    def process(self):
        self.processed_data = pd.DataFrame(self.raw_data)
        
if __name__ == "__main__":
    crawler = OpenCompassCrawler()
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
    