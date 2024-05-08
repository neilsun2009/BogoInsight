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
from BogoInsight.utils.logger import logger

class LLMSpecsCrawler(BaseCrawler):
    
    URL = "https://en.wikipedia.org/wiki/Large_language_model"
    
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
        'Gemini 1.0', 'Gemini 1.5', 'Gemma',
    ]
    
    AUXILIARY_INFOS = {
        'GPT-1': {
            'series first': True,
            'series lead': True,
        },
        'BERT': {
            'corpus size (B tokens)': 5.4,
            'series first': True,
            'series lead': True,
        },
        'T5': {
            'corpus size (B tokens)': 34,
            'series first': True,
            'series lead': True,
        },
        'Chinchilla': {
            'corpus size (B tokens)': 1400,
            'series first': True,
            'series lead': True,
        },
        'PaLM': {
            'corpus size (B tokens)': 768,
            'series first': True,
            'series lead': True,
        },
        'PaLM 2': {
            'period': pd.to_datetime('2023-05-10'),
            'input context window (K tkns)': 25.804,
            'max output tokens (K tkns)': 2.967,
            'input token price ($/M tkns)': 0.25,
            'output token price ($/M tkns)': 0.5,
            'corpus size (B tokens)': 3600,
            'series first': True,
            'series lead': True,
        },
        'Gemma': {
            'period': pd.to_datetime('2024-02-21'),
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 8.192,
            'input token price ($/M tkns)': 0,
            'output token price ($/M tkns)': 0,
            'corpus size (B tokens)': 6000,
            'series first': True,
            'series lead': True,
        },
        'Gemini 1.0': {
            'period': pd.to_datetime('2023-12-23'),
            'parameters (B)': 1500, # estimate
            'input context window (K tkns)': 91.728,
            'max output tokens (K tkns)': 22.937,
            'input token price ($/M tkns)': 0.125,
            'output token price ($/M tkns)': 0.375,
            'input image price ($/K imgs)': 2.5,
            'series first': True,
            'series lead': True,
        },
        'Gemini 1.5': {
            'period': pd.to_datetime('2024-02-15'),
            'parameters (B)': 2000, # estimate
            'input context window (K tkns)': 2800,
            'max output tokens (K tkns)': 22.937,
            'input token price ($/M tkns)': 2.5,
            'output token price ($/M tkns)': 7.5,
            'input image price ($/K imgs)': 2.65,
            'series first': True,
            'series lead': True,
        },
        'Ernie 3.0 Titan': {
            'corpus size (B tokens)': 4000,
            'series first': True,
            'series lead': True,
        },
        'LLaMA': {
            'corpus size (B tokens)': 1400,
            'series first': True,
            'series lead': True,
        },
        'Llama 2 13B': {
            'period': pd.to_datetime('2023-07-18'),
            'parameters (B)': 13,
            'input context window (K tkns)': 4.096,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 0.13,
            'output token price ($/M tkns)': 0.13,
            'corpus size (B tokens)': 2000,
            'series first': False,
            'series lead': False,
        },
        'Llama 2 70B': {
            'period': pd.to_datetime('2023-07-18'),
            'parameters (B)': 70,
            'input context window (K tkns)': 4.096,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 0.64,
            'output token price ($/M tkns)': 0.8,
            'corpus size (B tokens)': 2000,
            'series first': True,
            'series lead': True,
        },
        'Llama 3 8B': {
            'period': pd.to_datetime('2024-04-18'),
            'developer': 'Meta',
            'license': 'Llama 3 license',
            'parameters (B)': 8,
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 8.192,
            'input token price ($/M tkns)': 0.07,
            'output token price ($/M tkns)': 0.07,
            'corpus size (B tokens)': 15000,
            'series first': False,
            'series lead': False,
        },
        'Llama 3 70B': {
            'period': pd.to_datetime('2024-04-18'),
            'developer': 'Meta',
            'license': 'Llama 3 license',
            'parameters (B)': 70,
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 8.192,
            'input token price ($/M tkns)': 0.59,
            'output token price ($/M tkns)': 0.79,
            'corpus size (B tokens)': 15000,
            'series first': True,
            'series lead': True,
        },
        'PanGu-Σ': {
            'corpus size (B tokens)': 329,
            'series first': True,
            'series lead': True,
        },
        'Grok-1': {
            'series first': True,
            'series lead': True,
        },
        'Mistral 7B': {
            'period': pd.to_datetime('2023-09-27'),
            'input context window (K tkns)': 32.768,
            'max output tokens (K tkns)': 32.768,
            'input token price ($/M tkns)': 0,
            'output token price ($/M tkns)': 0,
            'series first': True,
            'series lead': True,
        },
        'Mixtral 8x7B': {
            'period': pd.to_datetime('2023-12-11'),
            'input context window (K tkns)': 32.768,
            'max output tokens (K tkns)': 32.768,
            'input token price ($/M tkns)': 0.24,
            'output token price ($/M tkns)': 0.24,
            'series first': True,
            'series lead': True,
        },
        'Mistral Medium': {
            'period': pd.to_datetime('2024-02-26'),
            'parameters (B)': 1000, # estimate
            'developer': 'Mistral AI',
            'license': 'Proprietary',
            'input context window (K tkns)': 32,
            'max output tokens (K tkns)': 32,
            'input token price ($/M tkns)': 2.7,
            'output token price ($/M tkns)': 8.1,
            'series first': False,
            'series lead': False,
        },
        'Mistral Large': {
            'period': pd.to_datetime('2024-02-26'),
            'parameters (B)': 1000, # estimate
            'developer': 'Mistral AI',
            'license': 'Proprietary',
            'input context window (K tkns)': 32,
            'max output tokens (K tkns)': 32,
            'input token price ($/M tkns)': 8,
            'output token price ($/M tkns)': 24,
            'series first': True,
            'series lead': True,
        },
        'Claude': {
            'period': pd.to_datetime('2022-11-28'),
            'input context window (K tkns)': 100,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 8,
            'output token price ($/M tkns)': 24,
            'corpus size (B tokens)': 400,
            'series first': True,
            'series lead': True,
        },
        'Claude 2': {
            'period': pd.to_datetime('2023-07-11'),
            'parameters (B)': 130, # estimate
            'input context window (K tkns)': 100,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 8,
            'output token price ($/M tkns)': 24,
            'series first': True,
            'series lead': True,
        },
        'Claude 2.1': {
            'period': pd.to_datetime('2023-11-23'),
            'parameters (B)': 130, # estimate
            'input context window (K tkns)': 200,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 8,
            'output token price ($/M tkns)': 24,
            'series first': True,
            'series lead': True,
        },
        'Claude 3 Haiku': {
            'period': pd.to_datetime('2024-03-04'),
            'parameters (B)': 2000, # estimate
            'input context window (K tkns)': 200,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 0.25,
            'output token price ($/M tkns)': 1.25,
            'input image price ($/K imgs)': 0.4,
            'series first': True,
            'series lead': True,
        },
        'Claude 3 Sonnet': {
            'period': pd.to_datetime('2024-03-04'),
            'parameters (B)': 2000, # estimate
            'input context window (K tkns)': 200,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 3,
            'output token price ($/M tkns)': 15,
            'input image price ($/K imgs)': 4.8,
            'series first': False,
            'series lead': False,
        },
        'Claude 3 Opus': {
            'period': pd.to_datetime('2024-03-04'),
            'parameters (B)': 2000, # estimate
            'input context window (K tkns)': 200,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 15,
            'output token price ($/M tkns)': 75,
            'input image price ($/K imgs)': 24,
            'series first': False,
            'series lead': False,
        },
        'GPT-2': {
            'corpus size (B tokens)': 10,
            'series first': True,
            'series lead': True,
        },
        'GPT-3': {
            'corpus size (B tokens)': 300,
            'series first': True,
            'series lead': True,
        },
        'GPT-3.5 Turbo': {
            'period': pd.to_datetime('2022-11-28'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 4.096,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 0.5,
            'output token price ($/M tkns)': 1.5,
            'series first': True,
            'series lead': False,
        },
        'GPT-3.5 Turbo 0301': {
            'period': pd.to_datetime('2023-03-01'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 4.096,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 1,
            'output token price ($/M tkns)': 2,
            'series first': False,
            'series lead': False,
        },
        'GPT-3.5 Turbo 16K 0613': {
            'period': pd.to_datetime('2023-06-13'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 16.385,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 3,
            'output token price ($/M tkns)': 4,
            'series first': False,
            'series lead': False,
        },
        'GPT-3.5 Turbo 16K 1106': {
            'period': pd.to_datetime('2023-11-06'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 16.385,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 1,
            'output token price ($/M tkns)': 2,
            'series first': False,
            'series lead': False,
        },
        'GPT-3.5 Turbo 16K 0125': {
            'period': pd.to_datetime('2024-01-25'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 16.385,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 0.5,
            'output token price ($/M tkns)': 1.5,
            'series first': False,
            'series lead': True,
        },
        'GPT-4': {
            'period': pd.to_datetime('2023-03-14'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 30,
            'output token price ($/M tkns)': 60,
            'series first': False,
            'series lead': False,
        },
        'GPT-4 32K': {
            'period': pd.to_datetime('2023-03-14'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 32.768,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 60,
            'output token price ($/M tkns)': 120,
            'series first': True,
            'series lead': False,
        },
        'GPT-4 0613': {
            'period': pd.to_datetime('2023-06-13'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 30,
            'output token price ($/M tkns)': 60,
            'series first': False,
            'series lead': False,
        },
        'GPT-4 32K 0613': {
            'period': pd.to_datetime('2023-06-13'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 32.768,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 60,
            'output token price ($/M tkns)': 120,
            'series first': False,
            'series lead': False,
        },
        'GPT-4 Turbo': {
            'period': pd.to_datetime('2023-11-06'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 128,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 10,
            'output token price ($/M tkns)': 30,
            'series first': False,
            'series lead': False,
        },
        'GPT-4 Turbo 0125': {
            'period': pd.to_datetime('2024-01-25'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 128,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 10,
            'output token price ($/M tkns)': 30,
            'series first': False,
            'series lead': False,
        },
        'GPT-4 Turbo 2024-04-09': {
            'period': pd.to_datetime('2024-04-09'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 128,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 10,
            'output token price ($/M tkns)': 30,
            'series first': False,
            'series lead': True,
        },
        'GPT-4 Vision Preview': {
            'period': pd.to_datetime('2023-09-25'),
            'developer': 'OpenAI',
            'license': 'Proprietary',
            'parameters (B)': 1760,
            'input context window (K tkns)': 128,
            'max output tokens (K tkns)': 4.096,
            'input token price ($/M tkns)': 10,
            'output token price ($/M tkns)': 30,
            'input image price ($/K imgs)': 14.45,
            'series first': True,
            'series lead': True,
        },
        'Ernie 3.5': {
            'period': pd.to_datetime('2023-06-27'),
            'developer': 'Baidu',
            'license': 'Proprietary',
            'parameters (B)': 175, # estimate
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 8.192,
            'input token price ($/M tkns)': 1.7,
            'output token price ($/M tkns)': 1.7,
            'series first': True,
            'series lead': True,
        },
        'Ernie 4.0': {
            'period': pd.to_datetime('2024-04-16'),
            'developer': 'Baidu',
            'license': 'Proprietary',
            'parameters (B)': 1750, # estimate
            'input context window (K tkns)': 8.192,
            'max output tokens (K tkns)': 8.192,
            'input token price ($/M tkns)': 2.1,
            'output token price ($/M tkns)': 4.2,
            'series first': True,
            'series lead': True,
        },
        'Qwen 1.8B': {
            'period': pd.to_datetime('2023-11-30'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 1.8,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0,
            'output token price ($/M tkns)': 0,
            'series first': False,
            'series lead': False,
        },
        'Qwen 7B': {
            'period': pd.to_datetime('2023-08-03'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 7,
            'input context window (K tkns)': 6,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0.85,
            'output token price ($/M tkns)': 0.85,
            'series first': False,
            'series lead': False,
        },
        'Qwen 14B': {
            'period': pd.to_datetime('2023-09-25'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 14,
            'input context window (K tkns)': 6,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 1.1,
            'output token price ($/M tkns)': 1.1,
            'series first': False,
            'series lead': False,
        },
        'Qwen 72B': {
            'period': pd.to_datetime('2023-11-30'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 72,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 2.8,
            'output token price ($/M tkns)': 2.8,
            'series first': True,
            'series lead': True,
        },
        'Qwen1.5 0.5B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 0.5,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0,
            'output token price ($/M tkns)': 0,
            'series first': False,
            'series lead': False,
        },
        'Qwen1.5 1.8B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 1.8,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0,
            'output token price ($/M tkns)': 0,
            'series first': False,
            'series lead': False,
        },
        'Qwen1.5 7B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 7,
            'input context window (K tkns)': 6,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0.85,
            'output token price ($/M tkns)': 0.85,
            'series first': False,
            'series lead': False,
        },
        'Qwen1.5 14B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 14,
            'input context window (K tkns)': 6,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 1.1,
            'output token price ($/M tkns)': 1.1,
            'series first': False,
            'series lead': False,
        },
        'Qwen1.5 32B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 32,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0, # temp
            'output token price ($/M tkns)': 0, # temp
            'series first': False,
            'series lead': False,
        },
        'Qwen1.5 72B': {
            'period': pd.to_datetime('2024-02-06'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 72,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 2.8,
            'output token price ($/M tkns)': 2.8,
            'series first': True,
            'series lead': False,
        },
        'Qwen1.5 110B': {
            'period': pd.to_datetime('2024-04-20'),
            'developer': 'Aliyun',
            'license': 'tongyi-qianwen',
            'parameters (B)': 110,
            'input context window (K tkns)': 30,
            'max output tokens (K tkns)': 2,
            'input token price ($/M tkns)': 0, # temp
            'output token price ($/M tkns)': 0, # temp
            'series first': False,
            'series lead': True,
        },
        'Moonshot V1 8K': {
            'period': pd.to_datetime('2023-11-16'),
            'developer': 'Moonshot',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 8,
            'max output tokens (K tkns)': 8,
            'input token price ($/M tkns)': 1.7,
            'output token price ($/M tkns)': 1.7,
            'series first': False,
            'series lead': False,
        },
        'Moonshot V1 32K': {
            'period': pd.to_datetime('2023-11-16'),
            'developer': 'Moonshot',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 32,
            'max output tokens (K tkns)': 32,
            'input token price ($/M tkns)': 3.4,
            'output token price ($/M tkns)': 3.4,
            'series first': False,
            'series lead': False,
        },
        'Moonshot V1 128K': {
            'period': pd.to_datetime('2023-11-16'),
            'developer': 'Moonshot',
            'license': 'Proprietary',
            'parameters (B)': 200,
            'input context window (K tkns)': 128,
            'max output tokens (K tkns)': 128,
            'input token price ($/M tkns)': 8.5,
            'output token price ($/M tkns)': 8.5,
            'series first': True,
            'series lead': True,
        },
    }
    
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
        for new_name in ['Llama 2 13B', 'Llama 2 70B']:
            new_row = row.copy()
            new_row['name'] = new_name
            df = pd.concat([df, new_row], ignore_index=True)
        df = df.drop(df[df['name'] == 'Llama 2'].index)

        df = df.set_index('name')
        
        # Add additional information
        # Convert AUXILIARY_INFOS to a DataFrame
        aux_df = pd.DataFrame.from_dict(self.AUXILIARY_INFOS, orient='index')
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

        # Set the name of the index column to 'name'
        df.index.name = 'name'
        
        # Reorder the columns
        top_columns = ['period', 'developer', 'parameters (B)', 
                       'input context window (K tkns)', 'max output tokens (K tkns)',
                       'input token price ($/M tkns)', 'output token price ($/M tkns)', 'input image price ($/K imgs)',
                       'source access']
        new_order = top_columns + [c for c in df.columns if c not in top_columns]
        df = df.reindex(new_order, axis=1)
        df = df.sort_values('period')

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