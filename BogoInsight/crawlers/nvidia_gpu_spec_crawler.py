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

class NvidiaGPUSpecsCrawler(BaseCrawler):
    
    URL = "https://en.wikipedia.org/wiki/List_of_Nvidia_graphics_processing_units"
    
    COLUMN_NAME_MAP_DESKTOP = {
        'Model': 'model',
        'Launch': 'period',
        'Process': 'fab model',
        'Core config': 'CUDA cores',
        'Memory - Size (GB)': 'memory (GB)',
        'Memory - Bandwidth (GB/s)': 'bandwidth (GB/s)',
        'Memory - Bus type': 'memory bus type',
        'Clock speeds - Base core clock (MHz)': 'base clock (MHz)',
        'Clock speeds - Boost core clock (MHz)': 'boost clock (MHz)',
        'Processing power (TFLOPS) - Double precision': 'processing power fp64 (TFLOPS)',
        'Processing power (TFLOPS) - Single precision': 'processing power fp32 (TFLOPS)',
        'Processing power (TFLOPS) - Half precision': 'processing power fp16 (TFLOPS)',
        'TDP (Watts)': 'TDP (Watts)',
        # '': '',
        # '': '',
    }
    
    COLUMN_NAME_MAP_DATA_CENTER = {
        'Model': 'model',
        'Launch': 'period',
        'Shaders - CUDA cores (total)': 'CUDA cores',
        'Memory - Size (GB)': 'memory (GB)',
        'Memory - Bandwidth (GB/s)': 'bandwidth (GB/s)',
        'Memory - Bus type': 'memory bus type',
        'Shaders - Base clock (MHz)': 'base clock (MHz)',
        'Shaders - Max boost clock (MHz)': 'boost clock (MHz)',
        'Processing power (TFLOPS) - Double precision (FMA)': 'processing power fp64 (TFLOPS)',
        'Processing power (TFLOPS) - Single precision (MAD or FMA)': 'processing power fp32 (TFLOPS)',
        'Processing power (TFLOPS) - Half precision Tensor Core FP32 Accumulate': 'processing power fp16 (TFLOPS)',
        'Micro- architecture': 'architecture',
        'TDP (W)': 'TDP (Watts)',
        # '': '',
        # '': '',
    }
    
    DATA_CENTER_ARCH_FAB_MAP = {
        'Pascal': 'TSMC 16FF',
        'Volta': 'TSMC 12FFN',
        'Turing': 'TSMC 12FFN',
        'Ampere': 'TSMC N7', # note that for Ampere, consumer & prof versions have diff fab processes
        'Hopper': 'TSMC 4N',
        'Ada Lovelace': 'TSMC 4N',
    }
    
    FAB_MODEL_NM_MAP = {
        'TSMC 16FF': 14,
        'TSMC 12FFN': 14,
        'Samsung 8LPP': 10,
        'TSMC N7': 7,
        'TSMC 4N': 5,
    }
    
    def __init__(self):
        super().__init__(
            topic='Nvidia GPU Specs',
            desc="""
                Specs on Nvidia GPUs that are crucial for machine learning.
            """,
            tags=['GPU', 'machine learning'],
            source_desc="""
                Wikipedia: https://en.wikipedia.org/wiki/List_of_Nvidia_graphics_processing_units
                Nvidia official website: https://www.nvidia.com/
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
        
        # Select different series of GPUs
        dfs = [
            self._parse_section(soup, 'GeForce_10_series', 
                                sel_model_names=[
                                    'GeForce GTX 1080', 
                                    'GeForce GTX 1080 Ti',
                                    'TITAN X Pascal',
                                    'TITAN Xp',
                                ],
                                append_value_map={
                                    'usage': 'desktop',
                                    'series': 'GeForce 10 series',
                                    'architecture': 'Pascal',
                                }),
            self._parse_section(soup, 'Volta_series', 
                                sel_model_names=[
                                    'Nvidia TITAN V',
                                ],
                                append_value_map={
                                    'usage': 'desktop',
                                    'series': 'Volta series',
                                    'architecture': 'Volta',
                                }),
            self._parse_section(soup, 'RTX_20_series', 
                                sel_model_names=[
                                    'GeForce RTX 2070',
                                    'GeForce RTX 2080',
                                    'GeForce RTX 2080 Ti',
                                    'Nvidia TITAN RTX', 
                                ],
                                append_value_map={
                                    'usage': 'desktop',
                                    'series': 'GeForce 20 series',
                                    'architecture': 'Turing',
                                }),
            self._parse_section(soup, 'RTX_30_series', 
                                sel_model_names=[
                                    'GeForce RTX 3070',
                                    'GeForce RTX 3070 Ti',
                                    'GeForce RTX 3080',
                                    'GeForce RTX 3080 Ti',
                                    'GeForce RTX 3090',
                                    'GeForce RTX 3090 Ti',
                                ],
                                append_value_map={
                                    'usage': 'desktop',
                                    'series': 'GeForce 30 series',
                                    'architecture': 'Ampere',
                                }),
            self._parse_section(soup, 'RTX_40_series', 
                                sel_model_names=[
                                    'GeForce RTX 4070',
                                    'GeForce RTX 4070 Ti',
                                    'GeForce RTX 4080',
                                    'GeForce RTX 4090',
                                ],
                                append_value_map={
                                    'usage': 'desktop',
                                    'series': 'GeForce 40 series',
                                    'architecture': 'Ada Lovelace',
                                }),
            self._parse_section(soup, 'Tesla', 
                                sel_model_names=[
                                    'P100 GPU accelerator (mezzanine)',
                                    'P100 GPU accelerator (12 GB card)',
                                    'P100 GPU accelerator (16 GB card)',
                                    'P4 GPU accelerator',
                                    'P40 GPU accelerator',
                                    'V100 GPU accelerator (mezzanine)',
                                    'V100 GPU accelerator (PCIe card)',
                                    'V100 GPU accelerator (PCIe FHHL card)',
                                    'T4 GPU accelerator (PCIe card)',
                                    'A100 GPU accelerator (PCIe card)',
                                    'A40 GPU accelerator (PCIe card)',
                                    'A30 GPU accelerator (PCIe card)',
                                    'A10 GPU accelerator (PCIe card)',
                                    'H100 GPU accelerator (PCIe card)',
                                    'H100 GPU accelerator (SXM card)',
                                    'L40 GPU accelerator',
                                ],
                                append_value_map={
                                    'usage': 'data center',
                                    'series': 'Data Center GPUs',
                                },
                                column_name_map=self.COLUMN_NAME_MAP_DATA_CENTER),
        ]
        
        self.raw_data = pd.concat(dfs)
        logger.info(f"Successfully crawled data for {self.topic}, {len(self.raw_data)} records found.")
       
        
    def process(self):
        assert isinstance(self.raw_data, pd.DataFrame), "Raw data is not of type pd.DataFrame."

        df = pd.DataFrame(self.raw_data)
        df = df.set_index('model')
        # Reorder the columns
        new_order = ['period', 'usage', 'series', 'architecture', 'fab (nm)'] + [c for c in df.columns if c not in ['period', 'usage', 'series', 'architecture', 'fab (nm)']]
        df = df.reindex(new_order, axis=1)

        self.processed_data = df
        
    def _parse_section(self, soup, header, sel_model_names, append_value_map, column_name_map=COLUMN_NAME_MAP_DESKTOP):
        # Find the section by title
        section = soup.find('span', {'class': 'mw-headline', 'id': header}).parent
        
        # Find the first table in the section
        table_html = section.find_next_sibling('table')

        # Convert the HTML table to a pandas DataFrame
        table = pd.read_html(str(table_html))[0]
        
        # Replace all \xa0 characters with a space
        table = table.replace('\xa0', ' ', regex=True)
        table = table.replace('\xad', '', regex=True)
        
        # Check if the columns are MultiIndex
        if isinstance(table.columns, pd.MultiIndex):
            # Join the levels of MultiIndex column names with "-"
            table.columns = [' - '.join(col).strip() if col[0] != col[1] else col[0] for col in table.columns.values]
        
        print(f"columns for {header}", table.columns)
        
        # Keep only the rows where the model column is in sel_model_names
        table = table[table['Model'].isin(sel_model_names)]
        
        # Filter out rows where 'Launch' is 'Unlaunched'
        table = table.loc[table['Launch'] != 'Unlaunched']
        
        # Process processing power columns
        # power_columns = ['processing power fp64 (TFLOPS)', 'processing power fp32 (TFLOPS)', 'processing power fp16 (TFLOPS)']
        # print(table[power_columns])
        for col in [column for column in table.columns if 'Processing power' in column]:
            # Replace 'No' with np.nan
            table.loc[table[col] == 'No', col] = np.nan
            table.loc[table[col] == 'Unknown', col] = np.nan
            # Split the string at the space or hyphen and keep only the first part
            table[col] = table[col].str.split(' ').str[0]
            table[col] = table[col].str.split('–').str[0]
            table[col] = table[col].str.split('‒').str[0]
            # Remove commas
            table[col] = table[col].str.replace(',', '')
            # table[col] = table[col].str.replace(' ', '')
            # Convert the column to float
            table[col] = table[col].astype(float)
        
        # convert units
        # gflop -> tflop
        gflop_columns = ['Processing power (GFLOPS) - Double precision', 
                        'Processing power (GFLOPS) - Single precision', 
                        'Processing power (GFLOPS) - Half precision',
                        'Processing power (GFLOPS) - Half precision Tensor Core FP32 Accumulate',
                        'Processing power (GFLOPS) - Single precision (MAD or FMA)',
                        'Processing power (GFLOPS) - Double precision (FMA)']
        for column in gflop_columns:
            if column in table.columns:
                # Rename the column and convert its values
                new_column_name = column.replace('GFLOPS', 'TFLOPS')
                table[new_column_name] = (table.pop(column) / 1000).round(3)
        
        # Rename columns and drop others
        # if 'TDP (W)' in table.columns:
        table.rename(columns={
            'TDP (W)': 'TDP (Watts)',
            'Clock speeds - Base core (MHz)': 'Clock speeds - Base core clock (MHz)',
            'Clock speeds - Boost core (MHz)': 'Clock speeds - Boost core clock (MHz)',
        }, inplace=True)
        table.rename(columns=column_name_map, inplace=True)
        table = table.filter(items=column_name_map.values())
        
        # Append new columns
        table = table.assign(**append_value_map)
        
        # Add fab info to data center GPUs
        if append_value_map['usage'] == 'data center':
            table['fab model'] = table['architecture'].map(self.DATA_CENTER_ARCH_FAB_MAP)
        table['fab model'] = table['fab model'].str.replace(r'\s*\[.*\]', '', regex=True)
        # Add a new column "fab (nm)"
        table['fab (nm)'] = table['fab model'].map(self.FAB_MODEL_NM_MAP).astype(int)
        
        # Change "CUDA cores" column
        table['CUDA cores'] = table['CUDA cores'].str.split(':').str[0].astype(int)
        
        # Change "boost clock (MHz)" column
        table['boost clock (MHz)'] = table['boost clock (MHz)'].astype(str).str.split(' ').str[0]
        table['boost clock (MHz)'] = table['boost clock (MHz)'].str.replace(',', '')
        table['boost clock (MHz)'] = table['boost clock (MHz)'].astype(int)
        
        # Change "TDP (Watts)" column
        table['TDP (Watts)'] = table['TDP (Watts)'].astype(str).str.split('-').str[0]
        table['TDP (Watts)'] = table['TDP (Watts)'].astype(int)

        # Convert the 'period' column to datetime
        table['period'] = pd.to_datetime(table['period'])
        
        # Find duplicate model names
        duplicates = table.duplicated('model', keep=False)

        # Add suffix to duplicate model names
        suffix = table[duplicates].groupby('model').cumcount().add(1).astype(str).radd(' v')
        suffix = suffix.fillna('')  # Fill NaN values with empty string
        table.loc[duplicates, 'model'] = table['model'] + suffix

        # Find rows where 'memory (GB)' column contains ' or '
        mask = table['memory (GB)'].astype(str).str.contains(' or ')
        if mask.any():
            # Create a copy of these rows
            table_copy = table[mask].copy()
            # In the original table, keep only the value before ' or '
            table.loc[mask, 'memory (GB)'] = table['memory (GB)'].str.split(' or ').str[0]
            table.loc[mask, 'model'] = table['model'] + ' - ' + table['memory (GB)'] + 'G'
            table.loc[mask, 'memory (GB)'] = table['memory (GB)'].astype(int)
            # In the copied table, keep only the value after ' or '
            table_copy['memory (GB)'] = table_copy['memory (GB)'].str.split(' or ').str[1]
            table_copy['model'] = table_copy['model'] + ' - ' + table_copy['memory (GB)'] + 'G'
            table_copy['memory (GB)'] = table_copy['memory (GB)'].astype(int)
            # Concatenate the original table and the copied table
            table = pd.concat([table, table_copy], ignore_index=True)

        # Handle the case where there is no duplicate for the first occurrence
        table['model'] = table['model'].str.replace(' v1', '', regex=False)
        return table
        
if __name__ == "__main__":
    crawler = NvidiaGPUSpecsCrawler()
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